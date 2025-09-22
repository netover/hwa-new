import re
from typing import Dict, List


class SemanticExtractor:
    """
    Um serviço simples para extrair intenções e entidades de uma consulta
    usando palavras-chave e expressões regulares.
    """
    def __init__(self) -> None:
        # Mapeamento de palavras-chave para intenções
        self.intent_keywords = {
            "get_job_status": ["status", "job", "situação"],
            "get_job_log": ["log", "saída", "output"],
            "get_system_status": ["sistema", "geral", "tws"],
            "help": ["ajuda", "help", "socorro"],
        }

        # Mapeamento de tipos de entidade para padrões de RegEx
        self.entity_patterns = {
            # Garante que o nome do job comece com uma letra ou underscore, e não seja puramente numérico.
            "job_name": re.compile(r"\b([A-Z_][A-Z0-9_]{3,})\b"),
            "date": re.compile(r"\b(\d{2}/\d{2}/\d{4})\b"), # Ex: 22/09/2025
        }

    def extract_intent(self, query: str) -> str:
        """Extrai a intenção mais provável com base em palavras-chave."""
        query_lower = query.lower()
        for intent, keywords in self.intent_keywords.items():
            if any(keyword in query_lower for keyword in keywords):
                return intent
        return "unknown"

    def extract_entities(self, query: str) -> List[Dict[str, str]]:
        """Extrai entidades conhecidas usando expressões regulares."""
        entities = []
        for entity_type, pattern in self.entity_patterns.items():
            matches = pattern.findall(query)
            for match in matches:
                entities.append({"type": entity_type, "value": match})
        return entities

# Instância única para ser usada na aplicação
semantic_extractor = SemanticExtractor()
