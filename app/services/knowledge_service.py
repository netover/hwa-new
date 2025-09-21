from pathlib import Path
from typing import Any, Dict, Optional

import pandas as pd


class KnowledgeBaseService:
    """
    Gerencia o carregamento e a consulta da base de conhecimento
    a partir de uma planilha Excel.
    """
    def __init__(self, excel_path: str | Path):
        self.kb_path = Path(excel_path)
        self.kb_df: Optional[pd.DataFrame] = None

    def load_kb(self) -> None:
        """
        Carrega a planilha Excel para um DataFrame do pandas.
        Inclui tratamento de erros para arquivo não encontrado ou inválido.
        """
        try:
            if not self.kb_path.is_file():
                print(f"⚠️  Arquivo da base de conhecimento não encontrado em: {self.kb_path}")
                self.kb_df = pd.DataFrame() # Inicia com DF vazio
                return

            print(f"🔄 Carregando base de conhecimento de {self.kb_path}...")
            self.kb_df = pd.read_excel(self.kb_path, engine='openpyxl')
            # Padroniza os nomes das colunas (ex: remove espaços, converte para minúsculas)
            self.kb_df.columns = self.kb_df.columns.str.strip().str.lower().str.replace(' ', '_')
            print("✅ Base de conhecimento carregada com sucesso.")

        except Exception as e:
            print(f"❌ Erro ao carregar a base de conhecimento: {e}")
            self.kb_df = pd.DataFrame() # Garante que kb_df não seja None

    def search_for_solution(self, job_name: str) -> Optional[Dict[str, Any]]:
        """
        Busca por uma solução para um determinado job na base de conhecimento.
        A busca é case-insensitive.
        """
        if self.kb_df is None or self.kb_df.empty:
            return None

        # Garante que a coluna 'job_name' exista
        if 'job_name' not in self.kb_df.columns:
            print("❌ Coluna 'job_name' não encontrada na base de conhecimento.")
            return None

        # Busca pelo nome do job, ignorando case
        result = self.kb_df[self.kb_df['job_name'].str.lower() == job_name.lower()]

        if not result.empty:
            # Retorna a primeira correspondência como um dicionário
            solution_data = result.iloc[0].to_dict()
            # Limpa valores NaN que não são serializáveis em JSON
            return {k: v if pd.notna(v) else None for k, v in solution_data.items()}

        return None
