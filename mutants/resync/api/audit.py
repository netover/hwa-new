# resync/api/audit.py
from typing import (  # Added Optional for Query parameters
    Any,
    Dict,
    List,
    Optional,
)

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from resync.core.audit_queue import audit_queue
from resync.core.knowledge_graph import (  # noqa: N813
    AsyncKnowledgeGraph as knowledge_graph,
)

router = APIRouter(prefix="/api/audit", tags=["audit"])
from typing import Annotated, Callable

MutantDict = Annotated[dict[str, Callable], "Mutant"]


def _mutmut_trampoline(orig, mutants, call_args, call_kwargs, self_arg=None):
    """Forward call to original or mutated function, depending on the environment"""
    import os

    mutant_under_test = os.environ["MUTANT_UNDER_TEST"]
    if mutant_under_test == "fail":
        from mutmut.__main__ import MutmutProgrammaticFailException

        raise MutmutProgrammaticFailException("Failed programmatically")
    elif mutant_under_test == "stats":
        from mutmut.__main__ import record_trampoline_hit

        record_trampoline_hit(orig.__module__ + "." + orig.__name__)
        result = orig(*call_args, **call_kwargs)
        return result
    prefix = orig.__module__ + "." + orig.__name__ + "__mutmut_"
    if not mutant_under_test.startswith(prefix):
        result = orig(*call_args, **call_kwargs)
        return result
    mutant_name = mutant_under_test.rpartition(".")[-1]
    if self_arg:
        # call to a class method where self is not bound
        result = mutants[mutant_name](self_arg, *call_args, **call_kwargs)
    else:
        result = mutants[mutant_name](*call_args, **call_kwargs)
    return result


class ReviewAction(BaseModel):
    memory_id: str
    action: str  # "approve" or "reject"


@router.get("/flags", response_model=List[Dict[str, Any]])
def get_flagged_memories(
    status: str = Query(
        "pending",
        description="Filter by audit status (pending, approved, rejected, all)",
    ),
    query: Optional[str] = Query(
        None,
        description="Search query in user_query or agent_response",
    ),
):
    """
    Retrieves memories from the audit queue based on status and search query.
    """
    try:
        if status == "all":
            memories = audit_queue.get_all_audits_sync()
        else:
            memories = audit_queue.get_audits_by_status_sync(status)

        if query:
            # Filter in Python for now, can be pushed to DB later
            query_lower = query.lower()
            memories = [
                m
                for m in memories
                if query_lower in m.get("user_query", "").lower()
                or query_lower in m.get("agent_response", "").lower()
            ]

        return memories
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error retrieving flagged memories: {e}"
        ) from e


@router.post("/review")
async def review_memory(review: ReviewAction):
    """
    Processes a human review action for a flagged memory, updating its status in the database.
    """
    if review.action == "approve":
        try:
            if not audit_queue.update_audit_status_sync(review.memory_id, "approved"):
                raise HTTPException(status_code=404, detail="Audit record not found.")

            await knowledge_graph.client.add_observations(
                review.memory_id, ["MANUALLY_APPROVED_BY_ADMIN"]
            )
            return {"status": "approved", "memory_id": review.memory_id}
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Error approving memory: {e}"
            ) from e

    elif review.action == "reject":
        try:
            if not audit_queue.update_audit_status_sync(review.memory_id, "rejected"):
                raise HTTPException(status_code=404, detail="Audit record not found.")

            await knowledge_graph.client.delete(review.memory_id)
            return {"status": "rejected", "memory_id": review.memory_id}
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Error rejecting memory: {e}"
            ) from e

    raise HTTPException(status_code=400, detail="Invalid action")


@router.get("/metrics", response_model=Dict[str, int])  # New endpoint for metrics
def get_audit_metrics():
    """
    Returns metrics for the audit queue (total pending, approved, rejected).
    """
    try:
        metrics = audit_queue.get_audit_metrics_sync()
        return metrics
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error retrieving audit metrics: {e}"
        ) from e
