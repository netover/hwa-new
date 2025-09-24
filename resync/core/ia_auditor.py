# resync/core/ia_auditor.py
import asyncio
import logging

from resync.core import audit_queue
from resync.core.audit_lock import audit_lock
from resync.core.knowledge_graph import AsyncKnowledgeGraph as knowledge_graph
from resync.core.utils.json_parser import parse_llm_json_response
from resync.core.utils.llm import call_llm
from resync.settings import settings

logger = logging.getLogger(__name__)


async def _validate_memory_for_analysis(mem: dict) -> bool:
    """Checks if a memory is valid for analysis."""
    memory_id = mem["id"]
    if await knowledge_graph.is_memory_already_processed(memory_id):
        logger.debug(f"Memory {memory_id} already processed, skipping.")
        return False

    if mem.get("rating") is not None and mem.get("rating") >= 3:
        logger.debug(
            f"Memory {memory_id} has high rating ({mem.get('rating')}), skipping."
        )
        return False

    if not mem.get("user_query") or not mem.get("agent_response"):
        logger.debug(
            f"Memory {memory_id} missing user_query or agent_response, skipping."
        )
        return False

    # Skip if memory is already approved by human
    if await knowledge_graph.is_memory_approved(memory_id):
        logger.debug(f"Memory {memory_id} already approved by human, skipping.")
        return False

    return True


async def _get_llm_analysis(user_query: str, agent_response: str) -> dict | None:
    """Gets the analysis of a memory from the LLM."""
    prompt = f'''
    You are an expert TWS (IBM MQ/Workload Scheduler) auditor.
    Evaluate if the agent's response is correct for the user's query.

    Query: "{user_query}"
    Response: "{agent_response}"

    Consider:
    - Technical errors? (e.g., suggesting /tmp cleanup for a permission error)
    - Irrelevant response?
    - Contradictory information?

    Return ONLY a JSON object in the format:
    {{ "is_incorrect": true/false, "confidence": 0.0-1.0, "reason": "string" }}
    '''
    try:
        # Increased max_tokens from 200 to 500 to allow for more detailed analysis
        # and comprehensive reasoning in the auditor's evaluation of agent responses
        result = await call_llm(
            prompt, model=settings.AUDITOR_MODEL_NAME, max_tokens=500
        )
        if not result:
            return None

        return parse_llm_json_response(
            result,
            required_keys=["is_incorrect", "confidence", "reason"],
        )
    except Exception as e:
        logger.warning(f"IA Auditor: LLM analysis failed: {e}")
        return None


async def _perform_action_on_memory(mem: dict, analysis: dict) -> tuple[str, dict] | None:
    """Performs the appropriate action on a memory based on the LLM analysis."""
    memory_id = mem["id"]
    if analysis.get("is_incorrect") and analysis.get("confidence", 0) > 0.85:
        logger.info(
            f"🚨 DELETING: ID {memory_id} | Confidence: {analysis.get('confidence', 0):.2f} | Reason: {analysis.get('reason', 'N/A')}"
        )
        success = await knowledge_graph.atomic_check_and_delete(memory_id)
        return ("delete", memory_id) if success else None

    elif analysis.get("is_incorrect") and analysis.get("confidence", 0) > 0.6:
        reason = analysis.get("reason", "N/A")
        confidence = analysis.get("confidence", 0)
        logger.warning(
            f"⚠️ FLAGGING: ID {memory_id} | Confidence: {confidence:.2f} | Reason: {reason}"
        )
        success = await knowledge_graph.atomic_check_and_flag(
            memory_id, reason, confidence
        )
        if success:
            mem["ia_audit_reason"] = reason
            mem["ia_audit_confidence"] = confidence
            return "flag", mem

    return None


async def analyze_memory(mem: dict) -> tuple[str, dict] | None:
    """Analyzes a single memory and returns an action if necessary."""
    memory_id = mem["id"]
    try:
        async with await audit_lock.acquire(memory_id, timeout=30):
            if not await _validate_memory_for_analysis(mem):
                return None

            # Check if memory is already flagged or approved before LLM analysis
            if await knowledge_graph.is_memory_flagged(memory_id):
                logger.debug(f"Memory {memory_id} already flagged by IA, skipping analysis.")
                return None

            if await knowledge_graph.is_memory_approved(memory_id):
                logger.debug(f"Memory {memory_id} already approved by human, skipping analysis.")
                return None

            analysis = await _get_llm_analysis(
                mem.get("user_query", ""), mem.get("agent_response", "")
            )
            if not analysis:
                return None

            return await _perform_action_on_memory(mem, analysis)

    except Exception as e:
        logger.error(
            f"IA Auditor: Error analyzing memory {memory_id}: {e}", exc_info=True
        )
        return None


async def analyze_and_flag_memories():
    """
    Analyzes recent memories, skipping those already reviewed, and flags or
    removes incorrect ones. Uses atomic operations with distributed locking
    to prevent race conditions and duplicate flagging.
    """
    logger.info("IA Auditor: Analyzing recent memories...")

    try:
        await audit_lock.cleanup_expired_locks(max_age=60)
    except Exception as e:
        logger.warning(f"IA Auditor: Error cleaning up expired locks: {e}")

    try:
        recent_memories = await knowledge_graph.get_all_recent_conversations(100)
    except Exception as e:
        logger.error(f"IA Auditor: Error searching memories: {e}", exc_info=True)
        return {"deleted": 0, "flagged": 0}

    tasks = [analyze_memory(mem) for mem in recent_memories]
    results = await asyncio.gather(*tasks)

    to_delete = []
    to_flag = []
    for result in results:
        if result:
            action, value = result
            if action == "delete":
                to_delete.append(value)
            elif action == "flag":
                to_flag.append(value)
                await audit_queue.add_audit_record(value)

    for mem_id in to_delete:
        await knowledge_graph.delete_memory(mem_id)

    logger.info(
        f"IA Auditor: Finished. Deleted: {len(to_delete)}, Flagged: {len(to_flag)}"
    )
    return {"deleted": len(to_delete), "flagged": len(to_flag)}
