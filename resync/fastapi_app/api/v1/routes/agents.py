
from fastapi import APIRouter
from ..models.response_models import AgentListResponse

router = APIRouter(tags=["Agents"])

@router.get("/")
def list_agents() -> AgentListResponse:
    """
    List all available agents
    """
    return AgentListResponse(agents=[], total=0)

# Note: /status route moved to status router to avoid conflicts
