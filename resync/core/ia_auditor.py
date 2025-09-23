# resync/core/ia_auditor.py
import re
import json
from datetime import datetime
import os
import asyncio
import logging

from resync.core.knowledge_graph import knowledge_graph
from resync.core.utils.llm import call_llm
from resync.core.utils.json_parser import parse_llm_json_response
from resync.settings import settings
from resync.core import audit_queue

logger = logging.getLogger(__name__)

async def analyze_and_flag_memories():
    """
    Analyzes recent memories, skipping those already reviewed, and flags or
    removes incorrect ones. Uses atomic operations with distributed locking
    to prevent race conditions and duplicate flagging.
    """
    logger.info("IA Auditor: Analyzing recent memories...")

    # Clean up any expired locks before starting
    try:
        await audit_queue.cleanup_expired_locks("memory:", max_age=60)
    except Exception as e:
        logger.warning(f"IA Auditor: Error cleaning up expired locks: {e}")

    try:
        # Use the new async method directly
        recent_memories = await knowledge_graph.get_all_recent_conversations(100)
    except Exception as e:
        logger.error(f"IA Auditor: Error searching memories: {e}", exc_info=True)
        return {"deleted": 0, "flagged": 0}

    to_delete = []
    to_flag = []

    async def analyze_memory(mem):
        memory_id = mem["id"]

        # Use distributed lock to prevent race conditions
        try:
            async with audit_queue.with_lock(f"memory:{memory_id}", timeout=30):
                # First check if already processed atomically
                if await knowledge_graph.is_memory_already_processed(memory_id):
                    logger.debug(f"Memory {memory_id} already processed, skipping.")
                    return None, None

                # Check if memory has high rating (skip if >= 3)
                if mem.get("rating") is not None and mem.get("rating") >= 3:
                    logger.debug(f"Memory {memory_id} has high rating ({mem.get('rating')}), skipping.")
                    return None, None

                user_query = mem.get("user_query", "")
                agent_response = mem.get("agent_response", "")

                if not user_query or not agent_response:
                    logger.debug(f"Memory {memory_id} missing user_query or agent_response, skipping.")
                    return None, None

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
                    result = await call_llm(prompt, model=settings.AUDITOR_MODEL_NAME, max_tokens=500)
                    if not result:
                        logger.warning(f"IA Auditor: LLM call failed for memory {memory_id}.")
                        return None, None

                    # Use robust JSON parser instead of regex
                    try:
                        analysis = parse_llm_json_response(result, required_keys=["is_incorrect", "confidence", "reason"])
                    except Exception as parse_error:
                        logger.warning(f"IA Auditor: Failed to parse JSON from LLM response for memory {memory_id}: {parse_error}. Raw response: {result}")
                        return None, None

                    if analysis.get("is_incorrect") and analysis.get("confidence", 0) > 0.85:
                        logger.info(f"🚨 DELETING: ID {memory_id} | Confidence: {analysis.get('confidence', 0):.2f} | Reason: {analysis.get('reason', 'N/A')}")

                        # Use atomic delete operation
                        success = await knowledge_graph.atomic_check_and_delete(memory_id)
                        return "delete", memory_id if success else None

                    elif analysis.get("is_incorrect") and analysis.get("confidence", 0) > 0.6:
                        reason = analysis.get('reason', 'N/A')
                        confidence = analysis.get('confidence', 0)
                        logger.warning(f"⚠️ FLAGGING: ID {memory_id} | Confidence: {confidence:.2f} | Reason: {reason}")

                        # Use atomic flag operation
                        success = await knowledge_graph.atomic_check_and_flag(memory_id, reason, confidence)
                        if success:
                            mem['ia_audit_reason'] = reason
                            mem['ia_audit_confidence'] = confidence
                            return "flag", mem
                        else:
                            return None, None

                except Exception as e:
                    logger.error(f"IA Auditor: Error analyzing memory {memory_id}: {e}", exc_info=True)
                    return None, None

        except Exception as lock_error:
            logger.error(f"IA Auditor: Failed to acquire lock for memory {memory_id}: {lock_error}")
            return None, None

        return None, None

    tasks = [analyze_memory(mem) for mem in recent_memories]
    results = await asyncio.gather(*tasks)

    for action, value in results:
        if action == "delete":
            to_delete.append(value)
        elif action == "flag":
            to_flag.append(value)
            await audit_queue.add_audit_record(value)

    # Use the new async delete method
    for mem_id in to_delete:
        await knowledge_graph.delete_memory(mem_id)

    logger.info(f"IA Auditor: Finished. Deleted: {len(to_delete)}, Flagged: {len(to_flag)}")
    return {"deleted": len(to_delete), "flagged": len(to_flag)}