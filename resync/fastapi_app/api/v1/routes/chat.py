
"""
Chat routes for FastAPI with RAG integration
"""
from fastapi import APIRouter, HTTPException, status, Depends, BackgroundTasks
from typing import Optional

# Import RAG components
from resync.RAG.microservice.core.embedding_service import EmbeddingService
from resync.RAG.microservice.core.vector_store import QdrantVectorStore, get_default_store
from resync.RAG.microservice.core.retriever import RagRetriever
from resync.RAG.microservice.core.ingest import IngestService

from ..dependencies import get_current_user, get_logger
from ..models.request_models import ChatMessageRequest, ChatHistoryQuery
from ..models.response_models import ChatMessageResponse

router = APIRouter()
logger = None  # Will be injected by dependency

# RAG components will be initialized lazily (when first used)
# to avoid event loop issues during module import
_rag_initialized = False
_rag_embedding_service = None
_rag_vector_store = None
_rag_retriever = None
_rag_ingest_service = None

async def _get_rag_components():
    """Lazy initialization of RAG components within async context"""
    global _rag_initialized, _rag_embedding_service, _rag_vector_store, _rag_retriever, _rag_ingest_service

    if not _rag_initialized:
        try:
            _rag_embedding_service = EmbeddingService()
            _rag_vector_store = get_default_store()
            _rag_retriever = RagRetriever(_rag_embedding_service, _rag_vector_store)
            _rag_ingest_service = IngestService(_rag_embedding_service, _rag_vector_store)
            _rag_initialized = True
            print("✅ RAG components initialized successfully (lazy)")
        except Exception as e:
            print(f"❌ Failed to initialize RAG components: {e}")
            _rag_embedding_service = None
            _rag_vector_store = None
            _rag_retriever = None
            _rag_ingest_service = None

    return _rag_embedding_service, _rag_vector_store, _rag_retriever, _rag_ingest_service

@router.post("/chat", response_model=ChatMessageResponse)
async def chat_message(
    request: ChatMessageRequest,
    background_tasks: BackgroundTasks,
    # Temporarily disabled authentication for testing
    # current_user: dict = Depends(get_current_user),
    logger_instance = Depends(get_logger)
):
    """Send chat message to agent"""
    global logger
    logger = logger_instance

    try:
        # Get RAG components (lazy initialization)
        _, _, rag_retriever, _ = await _get_rag_components()

        # RAG-enhanced chat logic
        if rag_retriever is not None:
            # Use RAG to retrieve relevant information
            relevant_docs = await rag_retriever.retrieve(
                query=request.message,
                top_k=3  # Get top 3 relevant documents
            )

            # Build response with retrieved context
            if relevant_docs:
                # Format retrieved information
                context_parts = []
                for i, doc in enumerate(relevant_docs[:3], 1):
                    payload = doc.get('payload', {})
                    content = payload.get('chunk_id', f'Document {i}')
                    score = doc.get('score', 0)
                    context_parts.append(f"[{i}] {content} (relevance: {score:.3f})")

                context = "\n".join(context_parts)
                response_message = f"Baseado nas informações encontradas:\n\n{context}\n\nComo posso ajudar com '{request.message}'?"
            else:
                response_message = f"Não encontrei informações relevantes sobre '{request.message}' na base de conhecimento. Como posso ajudar de outra forma?"
        else:
            # Fallback to echo if RAG is not available
            response_message = f"Echo (RAG não disponível): {request.message}"

        logger_instance.info(
            "chat_message_processed",
            # Temporarily using placeholder for user_id since auth is disabled
            user_id="test_user",
            agent_id=request.agent_id,
            message_length=len(request.message),
            rag_enabled=(rag_retriever is not None),
            docs_retrieved=len(relevant_docs) if 'relevant_docs' in locals() and relevant_docs else 0
        )

        return ChatMessageResponse(
            message=response_message,
            timestamp="2025-01-01T00:00:00Z",  # TODO: Use proper datetime
            agent_id=request.agent_id,
            is_final=True
        )

    except Exception as e:
        logger_instance.error("chat_message_error", error=str(e), user_id="test_user")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process chat message"
        )

@router.get("/chat/history")
async def chat_history(
    query_params: ChatHistoryQuery = Depends(),
    # Temporarily disabled authentication for testing
    # current_user: dict = Depends(get_current_user)
):
    """Get chat history for user/agent"""
    # TODO: Implement chat history retrieval from database
    return {
        "history": [],
        "agent_id": query_params.agent_id,
        "total_messages": 0
    }

@router.delete("/chat/history")
async def clear_chat_history(
    query_params: ChatHistoryQuery = Depends(),
    # Temporarily disabled authentication for testing
    # current_user: dict = Depends(get_current_user),
    logger_instance = Depends(get_logger)
):
    """Clear chat history for user/agent"""
    # TODO: Implement chat history clearing
    logger_instance.info(
        "chat_history_cleared",
        # Temporarily using placeholder for user_id since auth is disabled
        user_id="test_user",
        agent_id=query_params.agent_id
    )
    return {"message": "Chat history cleared successfully"}
