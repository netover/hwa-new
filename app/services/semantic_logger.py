import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

from sentence_transformers import SentenceTransformer

from app.services.knowledge_graph_manager import KnowledgeGraphManager


class SemanticLogger:
    """
    Logger que captura a semântica das interações para aprendizado contínuo,
    construção de um grafo de conhecimento e preparação de dados para fine-tuning.
    """

    def __init__(self, base_log_path: str = "logs"):
        self.base_log_path = Path(base_log_path)
        self.semantic_logs_path = self.base_log_path / "semantic_logs"
        self.exports_path = self.base_log_path / "exports"
        self.conversations_path = self.semantic_logs_path / "conversations"

        for path in [self.conversations_path, self.exports_path]:
            path.mkdir(parents=True, exist_ok=True)

        print("Initializing embedding model...")
        self.embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
        self.kg_manager = KnowledgeGraphManager(
            storage_path=self.semantic_logs_path / "knowledge_graph"
        )
        print("SemanticLogger initialized.")

    async def log_interaction(self, interaction_data: Dict[str, Any]) -> None:
        """
        Ponto de entrada principal para registrar uma interação completa,
        atualizar o grafo e preparar dados para fine-tuning.
        """
        # 1. Constrói a entrada semântica completa
        semantic_entry = self._build_semantic_entry(interaction_data)

        print(f"LOGGING INTERACTION: {semantic_entry.get('interaction_id', 'N/A')}")

        # 2. Salva o log da conversa
        await self._save_log_to_file(semantic_entry)

        # 3. Atualiza o grafo de conhecimento
        self.kg_manager.update_from_interaction(semantic_entry)

        # 4. Prepara e exporta dados para fine-tuning
        await self.prepare_fine_tuning_data(semantic_entry)

    def _build_semantic_entry(self, interaction_data: Dict[str, Any]) -> Dict[str, Any]:
        """Constrói a entrada de log rica com toda a semântica."""
        timestamp = datetime.now()
        session_id = interaction_data.get("session_id", "unknown_session")
        user_query = interaction_data.get("user_query", "")
        agent_response = interaction_data.get("agent_response", "")

        return {
            "timestamp": timestamp.isoformat(),
            "session_id": session_id,
            "interaction_id": f"{session_id}_{timestamp.strftime('%Y%m%d%H%M%S')}",
            "user_input": {
                "raw_query": user_query,
                "intent": interaction_data.get("classified_intent", "unknown"),
                "entities": interaction_data.get("entities", []),
                "embedding": self.embedding_model.encode(user_query).tolist(),
            },
            "agent_processing": {
                "agent_used": interaction_data.get("agent_name", "unknown"),
                "tools_called": interaction_data.get("tools_used", []),
            },
            "response": {
                "generated_text": agent_response,
                "embedding": self.embedding_model.encode(agent_response).tolist(),
            },
            "learning_signals": {
                "user_satisfaction": interaction_data.get("user_feedback"), # Placeholder
            },
        }

    async def _save_log_to_file(self, data: Dict[str, Any]) -> None:
        """Salva um registro de log em um arquivo JSONL."""
        try:
            date_str = datetime.fromisoformat(data["timestamp"]).strftime("%Y-%m-%d")
            session_id = data["session_id"]
            session_log_dir = self.conversations_path / date_str
            session_log_dir.mkdir(exist_ok=True)
            log_file = session_log_dir / f"session_{session_id}.jsonl"

            with open(log_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(data, ensure_ascii=False) + "\n")
        except Exception as e:
            print(f"❌ Erro ao salvar log semântico: {e}")

    async def prepare_fine_tuning_data(self, semantic_entry: Dict[str, Any]) -> None:
        """
        Formata e exporta uma interação de alta qualidade para o dataset de fine-tuning.
        """
        # Critério de qualidade inicial simples: a resposta do bot não é vazia
        if not semantic_entry.get("response", {}).get("generated_text"):
            return

        fine_tuning_example = {
            "messages": [
                {
                    "role": "system",
                    "content": "Você é um especialista em HCL Workload Automation (TWS).",
                },
                {
                    "role": "user",
                    "content": semantic_entry["user_input"]["raw_query"],
                },
                {
                    "role": "assistant",
                    "content": semantic_entry["response"]["generated_text"],
                },
            ]
        }

        file_path = self.exports_path / "fine_tuning_data.jsonl"
        try:
            with open(file_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(fine_tuning_example, ensure_ascii=False) + "\n")
        except Exception as e:
            print(f"❌ Erro ao exportar dados para fine-tuning: {e}")
