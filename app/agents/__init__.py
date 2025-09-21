from agno.agent import Agent

# Definição do Agente Despachante (Dispatcher)
# Este agente central recebe todas as requisições e as direciona para o especialista apropriado.
dispatcher = Agent(
    name="Dispatcher",
    # O modelo pode ser configurado dinamicamente no manager, aqui usamos um placeholder.
    model="openrouter/auto",
    role="Você é um despachante de tarefas inteligente para um sistema de monitoramento HCL Workload Automation (TWS).",
    instructions=[
        "Sua principal função é analisar a pergunta do usuário e decidir qual agente especialista deve respondê-la.",
        "Se a pergunta for sobre o status de jobs, jobstreams, engines ou qualquer outra entidade do TWS, encaminhe para o agente 'TWS_Monitor'.",
        "Se a pergunta for sobre a base de conhecimento, arquivos ou documentos, encaminhe para o 'Knowledge_Searcher'.",
        "Se a pergunta for uma saudação, conversa geral ou algo que não se encaixe em nenhuma especialidade, responda você mesmo de forma útil e concisa.",
        "Sempre responda em português do Brasil.",
    ],
    # O dispatcher normalmente não possui ferramentas, ele apenas delega a tarefa.
    tools=[],
)
