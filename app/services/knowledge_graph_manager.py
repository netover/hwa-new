import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

import networkx as nx


class KnowledgeGraphManager:
    """
    Gerencia a criação, atualização e persistência de um grafo de conhecimento
    baseado nas interações semânticas dos usuários e agentes.
    """
    def __init__(self, storage_path: str | Path = "logs/semantic_logs/knowledge_graph"):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        self.graph_file = self.storage_path / "knowledge_graph.json"

        self.graph = nx.MultiDiGraph()
        self._load_graph()
        print("KnowledgeGraphManager inicializado.")

    def _load_graph(self) -> None:
        """Carrega o grafo de um arquivo JSON se ele existir."""
        if self.graph_file.is_file():
            try:
                with open(self.graph_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.graph = nx.node_link_graph(data)
                print(f"Grafo de conhecimento carregado de {self.graph_file}")
            except Exception as e:
                print(f"❌ Erro ao carregar o grafo de conhecimento: {e}")

    def _save_graph(self) -> None:
        """Salva o estado atual do grafo em um arquivo JSON."""
        try:
            with open(self.graph_file, "w", encoding="utf-8") as f:
                data = nx.node_link_data(self.graph)
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"❌ Erro ao salvar o grafo de conhecimento: {e}")

    def update_from_interaction(self, semantic_entry: Dict[str, Any]) -> None:
        """
        Atualiza o grafo de conhecimento com base em uma única interação semântica.
        Esta é uma versão inicial que foca na co-ocorrência de entidades.
        """
        entities = semantic_entry.get("entities", [])
        intent = semantic_entry.get("intent", "unknown")
        timestamp = semantic_entry.get("timestamp", datetime.now().isoformat())

        # Adicionar/atualizar nós (entidades)
        for entity in entities:
            node_id = f"{entity.get('type', 'Untyped')}:{entity.get('value', 'Unknown')}"
            if not self.graph.has_node(node_id):
                self.graph.add_node(
                    node_id,
                    entity_type=entity.get("type"),
                    value=entity.get("value"),
                    first_seen=timestamp,
                    frequency=1,
                    contexts=[intent],
                )
            else:
                self.graph.nodes[node_id]["frequency"] += 1
                if intent not in self.graph.nodes[node_id]["contexts"]:
                    self.graph.nodes[node_id]["contexts"].append(intent)

        # Adicionar/atualizar arestas (relacionamentos de co-ocorrência)
        if len(entities) > 1:
            for i in range(len(entities)):
                for j in range(i + 1, len(entities)):
                    node1 = f"{entities[i].get('type', 'Untyped')}:{entities[i].get('value', 'Unknown')}"
                    node2 = f"{entities[j].get('type', 'Untyped')}:{entities[j].get('value', 'Unknown')}"
                    self.graph.add_edge(
                        node1,
                        node2,
                        relationship="co-occurrence",
                        intent=intent,
                        timestamp=timestamp,
                    )

        self._save_graph()
        print(f"Grafo de conhecimento atualizado com {len(entities)} entidades.")
