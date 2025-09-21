import asyncio
import json
from pathlib import Path
from typing import Any, Dict

from agno.agent import Agent
from agno.models.anthropic.claude import Claude
from agno.models.base import Model
from agno.models.openai.chat import OpenAIChat
from agno.models.openrouter.openrouter import OpenRouter

from app.core.watcher import watch_config_and_reload
from app.tools.tws_tool_readonly import TWSToolReadOnly

# Importa o agente dispatcher pré-configurado
from . import dispatcher as dispatcher_agent


class AgentManager:
    """Gerencia o ciclo de vida e a configuração dos agentes de IA."""

    def __init__(self) -> None:
        self.agents: Dict[str, Agent] = {}
        self.tools: Dict[str, Any] = {}
        self._config: Dict[str, Any] = {}
        self._watcher_task: asyncio.Task[None] | None = None

    @property
    def dispatcher(self) -> Agent | None:
        """Propriedade para acessar facilmente o agente dispatcher."""
        return self.agents.get("dispatcher")

    async def initialize_tools(self) -> None:
        """Inicializa e registra as ferramentas disponíveis."""
        self.tools["tws_readonly"] = TWSToolReadOnly()

    async def initialize(self) -> None:
        """
        Inicializa o gerenciador, carrega a configuração inicial e
        inicia o observador de arquivos para hot-reload.
        """
        print("Iniciando AgentManager...")
        await self.initialize_tools()

        config_path = Path("config/runtime.json")
        if not config_path.is_file():
            print(
                f"⚠️  Arquivo de configuração '{config_path}' não encontrado. Criando um padrão."
            )
            default_config: Dict[str, Any] = {
                "default_model": "openrouter/auto",
                "agents": {
                    "TWS_Monitor": {
                        "enabled": True,
                        "provider": "openrouter",
                        "tools": ["tws_readonly"],
                        "role": "Especialista em monitoramento do HCL Workload Automation (TWS).",
                        "instructions": [
                            "Use a ferramenta tws_readonly para responder perguntas sobre status de jobs, jobstreams e engines."
                        ],
                    }
                },
            }
            config_path.write_text(json.dumps(default_config, indent=2))

        # Carrega a configuração inicial
        await self.reload_agents_from_file(config_path)

        # Inicia a tarefa de observar o arquivo de configuração em background
        if not self._watcher_task or self._watcher_task.done():
            self._watcher_task = asyncio.create_task(
                watch_config_and_reload(config_path, self.reload_agents_from_file)
            )
        print("✅ AgentManager inicializado e watcher de configuração ativo.")

    def _get_model_instance(self, agent_config: Dict[str, Any], default_model_id: str) -> Model:
        """Factory function to create a model instance based on provider."""
        provider = agent_config.get("provider", "openrouter")
        model_id = agent_config.get("model", default_model_id)

        # Mapeamento de provedores para classes de modelo
        provider_map = {
            "openrouter": OpenRouter,
            "openai": OpenAIChat,
            "anthropic": Claude,
        }

        model_class = provider_map.get(provider)
        if not model_class:
            print(f"⚠️ Provedor de modelo desconhecido: '{provider}'. Usando OpenRouter como padrão.")
            model_class = OpenRouter

        return model_class(id=model_id, temperature=agent_config.get("temperature", 0.3))

    async def reload_agents_from_file(
        self, config_path_or_new_config: Path | Dict[str, Any]
    ) -> None:
        """Callback para recarregar agentes a partir de um arquivo ou de um novo dicionário de configuração."""
        if isinstance(config_path_or_new_config, Path):
            print(f"🔄 Recarregando configuração de '{config_path_or_new_config}'...")
            try:
                self._config = json.loads(config_path_or_new_config.read_text())
            except (json.JSONDecodeError, FileNotFoundError) as e:
                print(f"❌ Erro ao ler o arquivo de configuração: {e}. Nenhuma alteração feita.")
                return
        else:
            print("🔄 Recarregando configuração a partir de novos dados...")
            self._config = config_path_or_new_config

        self.agents.clear()

        agents_config = self._config.get("agents", {})
        default_model_id = self._config.get("default_model", "openrouter/auto")

        # Configura o dispatcher
        dispatcher_config = agents_config.get("dispatcher", {})
        dispatcher_agent.model = self._get_model_instance(dispatcher_config, default_model_id)
        self.agents["dispatcher"] = dispatcher_agent

        # Cria agentes especialistas
        for agent_name, agent_config in agents_config.items():
            if agent_name != "dispatcher" and agent_config.get("enabled", False):
                agent_tools = [
                    self.tools[tool_name]
                    for tool_name in agent_config.get("tools", [])
                    if tool_name in self.tools
                ]

                self.agents[agent_name] = Agent(
                    name=agent_name,
                    model=self._get_model_instance(agent_config, default_model_id),
                    tools=agent_tools,
                    role=agent_config.get("role"),
                    instructions=agent_config.get("instructions"),
                )
                print(f"  -> Agente '{agent_name}' carregado com o modelo '{agent_config.get('model')}'.")

        print("✅ Agentes recarregados com sucesso.")


# Cria uma instância única do gerenciador para ser usada em toda a aplicação.
reg = AgentManager()
