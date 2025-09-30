# resync/core/ia_auditor.py
import asyncio
import logging
from typing import Any, Dict, List, Optional, Tuple, Union

from resync.core.audit_queue import AsyncAuditQueue
from resync.core.audit_lock import DistributedAuditLock
from resync.core.exceptions import (
    AuditError,
    DatabaseError,
    KnowledgeGraphError,
    LLMError,
)
from resync.core.knowledge_graph import AsyncKnowledgeGraph
from resync.core.utils.json_parser import parse_llm_json_response
from resync.core.utils.llm import call_llm
from resync.settings import settings

logger = logging.getLogger(__name__)

# Initialize singleton instances
knowledge_graph = AsyncKnowledgeGraph()
audit_lock = DistributedAuditLock()
audit_queue = AsyncAuditQueue()

# --- Constants for IA Auditor Logic ---
AUDIT_DELETION_CONFIDENCE_THRESHOLD = 0.85
AUDIT_FLAGGING_CONFIDENCE_THRESHOLD = 0.6
AUDIT_HIGH_RATING_THRESHOLD = 3
RECENT_MEMORIES_FETCH_LIMIT = 100


async def _validate_memory_for_analysis(mem: Dict[str, Any]) -> bool:
    """Checks if a memory is valid for analysis."""
    memory_id = str(mem.get("id", ""))
    if await knowledge_graph.is_memory_already_processed(memory_id):
        logger.debug(f"Memory {memory_id} already processed, skipping.")
        return False

    rating = mem.get("rating")
    if (
        rating is not None
        and isinstance(rating, (int, float))
        and rating >= AUDIT_HIGH_RATING_THRESHOLD
    ):
        logger.debug(f"Memory {memory_id} has high rating ({rating}), skipping.")
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


async def _get_llm_analysis(
    user_query: str, agent_response: str
) -> Optional[Dict[str, Any]]:
    """Gets the analysis of a memory from the LLM."""
    prompt = f"""
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
    """
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
        logger.error("IA Auditor: LLM analysis failed: %s", e, exc_info=True)
        # Encapsulate the original error in a domain-specific one
        raise LLMError("Failed to get LLM analysis for memory audit") from e


async def _perform_action_on_memory(
    mem: Dict[str, Any], analysis: Dict[str, Any]
) -> Optional[Tuple[str, Union[str, Dict[str, Any]]]]:
    """Performs the appropriate action on a memory based on the LLM analysis."""
    memory_id = str(mem.get("id", ""))
    confidence = float(analysis.get("confidence", 0))

    if (
        analysis.get("is_incorrect")
        and confidence > AUDIT_DELETION_CONFIDENCE_THRESHOLD
    ):
        logger.info(
            f"🚨 DELETING: ID {memory_id} | Confidence: {confidence:.2f} | Reason: {analysis.get('reason', 'N/A')}"
        )
        success = await knowledge_graph.atomic_check_and_delete(memory_id)
        return ("delete", memory_id) if success else None

    elif (
        analysis.get("is_incorrect")
        and confidence > AUDIT_FLAGGING_CONFIDENCE_THRESHOLD
    ):
        reason = str(analysis.get("reason", "N/A"))
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


async def analyze_memory(
    mem: Dict[str, Any],
) -> Optional[Tuple[str, Union[str, Dict[str, Any]]]]:
    """Analyzes a single memory and returns an action if necessary."""
    memory_id = str(mem.get("id", ""))
    try:
        async with await audit_lock.acquire(memory_id, timeout=30):
            if not await _validate_memory_for_analysis(mem):
                return None

            # Check if memory is already flagged or approved before LLM analysis
            if await knowledge_graph.is_memory_flagged(memory_id):
                logger.debug(
                    f"Memory {memory_id} already flagged by IA, skipping analysis."
                )
                return None

            if await knowledge_graph.is_memory_approved(memory_id):
                logger.debug(
                    f"Memory {memory_id} already approved by human, skipping analysis."
                )
                return None

            analysis = await _get_llm_analysis(
                str(mem.get("user_query", "")), str(mem.get("agent_response", ""))
            )
            if not analysis:
                return None

            return await _perform_action_on_memory(mem, analysis)

    except LLMError as e:
        # Error already logged in _get_llm_analysis, just bubble it up if needed
        logger.warning("IA Auditor: Skipping memory %s due to LLM failure.", memory_id)
        return None
    except AuditError as e:
        # Lock acquisition failure
        logger.warning(
            "IA Auditor: Could not acquire lock for memory %s: %s", memory_id, e
        )
        return None
    except Exception:
        # Catch any other unexpected errors during the analysis of a single memory
        logger.error(
            "IA Auditor: Unexpected error analyzing memory %s", memory_id, exc_info=True
        )
        return None


async def _cleanup_locks() -> None:
    """Safely cleans up expired audit locks."""
    try:
        await audit_lock.cleanup_expired_locks(max_age=60)
    except Exception:
        logger.warning("IA Auditor: Error cleaning up expired locks.", exc_info=True)


async def _fetch_recent_memories() -> Optional[List[Dict[str, Any]]]:
    """Fetches recent conversations from the knowledge graph."""
    try:
        return await knowledge_graph.get_all_recent_conversations(
            RECENT_MEMORIES_FETCH_LIMIT
        )
    except (KnowledgeGraphError, DatabaseError) as e:
        logger.error(
            "IA Auditor: Could not fetch memories from the database: %s",
            e,
            exc_info=True,
        )
        return None


async def _analyze_memories_concurrently(
    memories: List[Dict[str, Any]],
) -> List[Optional[Tuple[str, Union[str, Dict[str, Any]]]]]:
    """Analyzes a list of memories in parallel."""
    tasks = [analyze_memory(mem) for mem in memories]
    return await asyncio.gather(*tasks)


async def _process_analysis_results(
    results: List[Optional[Tuple[str, Union[str, Dict[str, Any]]]]],
) -> Tuple[List[str], List[Dict[str, Any]]]:
    """Processes the results from memory analysis, sorting them into actions."""
    to_delete: List[str] = []
    to_flag: List[Dict[str, Any]] = []
    for result in results:
        if result:
            action, value = result
            if action == "delete" and isinstance(value, str):
                to_delete.append(value)
            elif action == "flag" and isinstance(value, dict):
                to_flag.append(value)
                await audit_queue.add_audit_record(value)
    return to_delete, to_flag


async def analyze_and_flag_memories() -> Dict[str, Union[int, str]]:
    """
    Analyzes recent memories, skipping those already reviewed, and flags
    or removes incorrect ones. Uses atomic operations with distributed locking
    to prevent race conditions and duplicate flagging.
    """
    logger.info("IA Auditor: Analyzing recent memories...")
    await _cleanup_locks()

    recent_memories = await _fetch_recent_memories()
    if recent_memories is None:
        return {"deleted": 0, "flagged": 0, "error": "database_fetch_failed"}

    analysis_results = await _analyze_memories_concurrently(recent_memories)
    to_delete, to_flag = await _process_analysis_results(analysis_results)

    for mem_id in to_delete:
        await knowledge_graph.delete_memory(mem_id)

    logger.info(
        "IA Auditor: Finished. Deleted: %d, Flagged: %d", len(to_delete), len(to_flag)
    )
    return {"deleted": len(to_delete), "flagged": len(to_flag)}
