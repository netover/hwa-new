# Resync: AI-Powered HWA/TWS Interface

## Propósito Principal

O Resync é uma interface de conversação inteligente, alimentada por Inteligência Artificial, para comunicação com o scheduler de cargas de trabalho **HCL Workload Automation (HWA)**, anteriormente conhecido como IBM Tivoli Workload Scheduler (TWS).

O objetivo é substituir a complexa navegação em painéis por uma interação simples e em linguagem natural, centralizando a informação e acelerando a resolução de problemas.

## Como Funciona

O coração do programa é a integração direta com o TWS através de um agente de IA que segue um fluxo claro:

1.  **Pergunta em Linguagem Natural:** Um operador pergunta ao chatbot, por exemplo: *"Qual o status do job `XYZ`?"* ou *"Mostre os jobs que falharam hoje"*.
2.  **Ação Dupla da IA:** O sistema executa duas ações em paralelo:
    *   **Chamada de API em Tempo Real:** O agente de IA executa uma chamada à API do HWA/TWS para obter o status atual e real do job solicitado.
    *   **Consulta à Base de Conhecimento (RAG):** Simultaneamente, ele consulta uma base de conhecimento interna (inicialmente um arquivo Excel, mas projetada para ser extensível) que contém informações adicionais, como procedimentos para tratamento de erros, contatos dos responsáveis e documentação relevante para aquele job.
3.  **Resposta Consolidada:** O chatbot retorna uma resposta única e enriquecida para o operador, combinando o status ao vivo do TWS com as informações contextuais e os procedimentos da base de conhecimento.

## Referências Oficiais

*   **Página do Produto:** [HCL Workload Automation](https://www.hcl-software.com/workload-automation)
*   **Documentação Oficial:** [HCL Workload Automation Documentation](https://help.hcltechsw.com/workload-automation/v10.2.3/index.html)

---
<br>

# Resync: O Centro de Comando Inteligente para HCL Workload Automation

**Resync não é apenas um dashboard. É uma plataforma de inteligência operacional projetada para transformar a maneira como você gerencia, monitora e soluciona problemas em seu ambiente HCL Workload Automation (TWS).**

---

## O Problema: A Complexidade da Operação TWS Tradicional

Gerenciar um ambiente TWS robusto é uma tarefa complexa que tradicionalmente envolve:

-   **Falta de Visibilidade Centralizada:** Operadores precisam navegar por múltiplas telas e terminais para obter uma visão completa do estado do sistema.
-   **Diagnóstico Lento e Reativo:** Quando um job falha (`ABEND`), inicia-se uma caça manual por logs, documentação e especialistas, resultando em um alto **MTTR (Mean Time to Resolution)**.
-   **Conhecimento Centralizado:** A expertise para resolver problemas complexos geralmente reside em alguns poucos especialistas, criando gargalos e riscos operacionais.
-   **Tarefas Repetitivas e Manuais:** A equipe gasta um tempo valioso em verificações de status e diagnósticos de rotina, em vez de focar em melhorias estratégicas.

## A Solução: Inteligência, Velocidade e Automação com Resync

Resync aborda esses desafios de frente, aplicando o que há de mais moderno em Inteligência Artificial e engenharia de software para entregar uma experiência de gerenciamento sem precedentes.

### ✨ Principais Recursos Estratégicos

#### 1. **Dashboard Unificado em Tempo Real**
Tenha uma visão completa e ao vivo do seu ambiente TWS em uma única tela. Monitore o status do sistema, dos motores e dos jobs mais recentes sem precisar sair da interface. A informação vem até você.

#### 2. **Chat com IA Especialista em TWS**
Faça perguntas em linguagem natural e obtenha respostas instantâneas. Em vez de navegar por menus complexos, simplesmente pergunte:
-   *"Qual o status do job `FINAL_BATCH_PAYROLL`?"*
-   *"Mostre-me os jobs que falharam nas últimas 3 horas."*
-   *"Resuma a saúde do ambiente."*

#### 3. **Diagnóstico Automático com RAG (Retrieval-Augmented Generation)**
Este é o nosso maior diferencial. Quando um job falha, o Resync não apenas informa o erro. Ele **automaticamente** consulta uma base de conhecimento (agora baseada em **Mem0 AI e Qdrant**) e enriquece a resposta com:
-   **Soluções Conhecidas:** Passos de troubleshooting baseados em incidentes passados.
-   **Owner do Processo:** Contato do responsável para uma resolução mais rápida.
-   **Procedimentos Relevantes:** Links para a documentação ou procedimentos operacionais padrão.

#### 4. **Inteligência Adaptativa e Aprendizado Contínuo**
Cada interação com o Resync é registrada e analisada semanticamente. O sistema aprende com as perguntas dos usuários e os problemas que resolve, criando um **Knowledge Graph** que o torna mais inteligente e preciso com o tempo. O **IA Auditor** monitora e refina essa base de conhecimento, sinalizando ou removendo memórias de baixa qualidade, e o **Dashboard de Revisão Humana** permite a curadoria final.

#### 5. **Arquitetura Robusta, Segura e Extensível**
Construído sobre uma base sólida com FastAPI, AGNO e as melhores práticas de software, o Resync é:
-   **Seguro:** Opera em modo **read-only** para operações no TWS, garantindo que não haja risco de comandos destrutivos. O `IA Auditor` pode remover memórias incorretas da base de conhecimento interna, mas não afeta o TWS.
-   **Estável:** Possui um cliente de API otimizado com connection pooling e retries para garantir a comunicação com o TWS.
-   **Extensível:** A arquitetura de agentes permite adicionar novas ferramentas e especialidades de IA com facilidade.

---

## 🚀 Vantagens Competitivas: O Valor do Resync

| Vantagem | Sem Resync (Método Tradicional) | Com Resync (Operação Inteligente) |
| :--- | :--- | :--- |
| **Resolução de Falhas (MTTR)** | Horas ou dias de análise manual. | **Segundos** para diagnóstico e sugestão de solução. |
| **Visibilidade** | Fragmentada, múltiplas ferramentas. | **Unificada e em tempo real** em um único dashboard. |
| **Abordagem** | Reativa (age após o problema). | **Proativa** (identifica e contextualiza o problema instantaneamente).|
| **Conhecimento** | Centralizado em especialistas. | **Democratizado** e acessível a toda a equipe via IA. |
| **Eficiência da Equipe** | Focada em tarefas manuais e repetitivas. | Focada em **melhorias estratégicas e otimização**. |

---

## 🛠 Quick Start (Guia Técnico)

### 1. Pré-requisitos
- Python 3.13+
- Acesso a um ambiente HCL Workload Automation (ou execute em modo mock).

### 2. Instalação
Clone o repositório:
'''bash
git clone https://github.com/netover/hwa-new-1.git
cd hwa-new-1
'''

Crie um ambiente virtual e instale as dependências:
'''bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
'''

### 3. Configuração
Crie um arquivo `.env` na raiz do projeto a partir do exemplo `.env.example`. Este arquivo centraliza todas as configurações sensíveis e de ambiente.

#### Configurações Principais

*   `TWS_HOST`, `TWS_PORT`, `TWS_USER`, `TWS_PASSWORD`: Credenciais para a conexão com a API do HWA/TWS.
*   `TWS_MOCK_MODE`: Defina como `True` para usar dados de exemplo (`mock_tws_data.json`) sem precisar de uma conexão real com o TWS. Ideal para desenvolvimento.
*   `APP_ENV`: Define o perfil da aplicação (`development` ou `production`).
*   `LLM_ENDPOINT`, `LLM_API_KEY`, `AGENT_MODEL_NAME`, `AUDITOR_MODEL_NAME`: Configurações do provedor de LLM. Veja exemplos detalhados abaixo.

---

#### Exemplos de Configuração do LLM

Graças à biblioteca `litellm`, você pode configurar o sistema para usar tanto LLMs rodando localmente quanto modelos acessados via API na nuvem. A escolha é feita através das variáveis de ambiente.

##### Exemplo 1: Usando um LLM Local com Ollama

Ideal para desenvolvimento, testes e ambientes que exigem que os dados não saiam da sua rede.

'''env
# Aponta para o endpoint local do Ollama
LLM_ENDPOINT=http://localhost:11434/v1

# Chave de API não é necessária para Ollama
LLM_API_KEY=

# Nome do modelo que você baixou com "ollama pull"
AGENT_MODEL_NAME=llama3
AUDITOR_MODEL_NAME=llama3
'''

---

A seguir, exemplos de como usar provedores de nuvem via API.

##### Exemplo 2: Usando a API da OpenAI

Para usar modelos de alta performance como GPT-4o diretamente da OpenAI.

'''env
# O endpoint pode ser omitido, pois a litellm usará o padrão da OpenAI
LLM_ENDPOINT=

# Sua chave de API da OpenAI
LLM_API_KEY=sk-proj-...

# Especifique os modelos desejados
AGENT_MODEL_NAME=gpt-4o
AUDITOR_MODEL_NAME=gpt-4o-mini
'''

##### Exemplo 3: Usando OpenRouter

Para acessar uma vasta gama de modelos de diferentes provedores (Google, Mistral, Anthropic, etc.) com uma única API.

'''env
# Aponta para o endpoint da API do OpenRouter
LLM_ENDPOINT=https://openrouter.ai/api/v1

# Sua chave de API do OpenRouter
LLM_API_KEY=sk-or-v1-abc...xyz

# Especifique o modelo desejado, prefixando com "openrouter/"
AGENT_MODEL_NAME=openrouter/google/gemini-pro-1.5
AUDITOR_MODEL_NAME=openrouter/google/gemini-pro-1.5
'''

##### Exemplo 4: Usando a API da NVIDIA NIM

Para usar os modelos otimizados da NVIDIA através de sua API. A integração é simples pois a API da NVIDIA também é compatível com o padrão da OpenAI.

'''env
# 1. Aponte para o endpoint da API da NVIDIA
LLM_ENDPOINT=https://integrate.api.nvidia.com/v1

# 2. Insira sua chave de API da NVIDIA
LLM_API_KEY=nvapi-abc...xyz

# 3. Especifique o ID do modelo da NVIDIA
AGENT_MODEL_NAME=meta/llama3-8b-instruct
AUDITOR_MODEL_NAME=meta/llama3-8b-instruct
'''

---

#### Precedência e Como Forçar uma Configuração

**A regra é simples: o nome do modelo (`AGENT_MODEL_NAME`) é o que manda.**

A biblioteca `litellm` decide para qual provedor enviar a requisição com base no formato do nome do modelo, não em qual variável de ambiente está preenchida.

##### Como Forçar o Uso de um LLM Local (Ex: Ollama)

Para garantir que o sistema use seu LLM local, defina um **nome de modelo genérico** (sem prefixos) e aponte o `LLM_ENDPOINT` para seu servidor local.

'''env
# 1. Aponte para o endpoint local
LLM_ENDPOINT=http://localhost:11434/v1

# 2. Defina um nome de modelo genérico (ex: 'llama3')
AGENT_MODEL_NAME=llama3

# Mesmo que a chave de API abaixo esteja preenchida, ela será ignorada
# porque o nome do modelo não direciona para um provedor de API.
LLM_API_KEY=sk-or-v1-abc...xyz
'''

##### Como Forçar o Uso de um LLM Externo via API (Ex: OpenRouter)

Para garantir que o sistema use uma API externa, use o **prefixo específico do provedor** no nome do modelo (se aplicável, como no OpenRouter) ou simplesmente configure o `LLM_ENDPOINT` e `LLM_API_KEY` para o provedor desejado. O prefixo no nome do modelo sempre terá prioridade sobre o `LLM_ENDPOINT`.

'''env
# 1. Use o prefixo do provedor no nome do modelo
AGENT_MODEL_NAME=openrouter/google/gemini-pro-1.5

# 2. Defina a chave de API correspondente
LLM_API_KEY=sk-or-v1-abc...xyz

# Mesmo que o endpoint local abaixo esteja preenchido, ele será ignorado
# porque o prefixo 'openrouter/' força o uso da API externa.
LLM_ENDPOINT=http://localhost:11434/v1
'''

### 4. Executando a Aplicação
Para iniciar o servidor backend:

**Modo Desenvolvimento (com Mock TWS):**
'''bash
# Certifique-se que TWS_MOCK_MODE=True e APP_ENV=development no seu .env
uvicorn resync.main:app --reload --host 0.0.0.0 --port 8000
'''
A aplicação estará disponível em `http://localhost:8000`.

**Modo Produção (com TWS real):**
'''bash
# Certifique-se que TWS_MOCK_MODE=False e APP_ENV=production no seu .env
# E que as variáveis TWS_HOST, TWS_PORT, TWS_USER, TWS_PASSWORD estejam configuradas
uvicorn resync.main:app --host 0.0.0.0 --port 8000
'''

### 5. Acessando as Interfaces
*   **Dashboard Principal:** `http://localhost:8000/dashboard`
*   **Chat com IA:** `http://localhost:8000/` (redireciona para o dashboard)
*   **Revisão de Memórias (IA Auditor):** `http://localhost:8000/revisao`
*   **Métricas Prometheus:** `http://localhost:8000/api/metrics`
*   **Documentação da API (Swagger UI):** `http://localhost:8000/docs`

### 6. Executando Testes
Para rodar os testes unitários e a análise estática:
'''bash
# Rodar testes unitários
make test

# Rodar linters e type checker
make fmt
'''

### 7. Docker (Opcional)
O projeto inclui um Dockerfile para containerização, mas o uso de Docker é opcional. Você pode executar a aplicação diretamente com Uvicorn conforme descrito na seção 4.
