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
```bash
git clone https://github.com/netover/hwa-new-1.git
cd hwa-new-1
```

Crie um ambiente virtual e instale as dependências:
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 3. Configuração
Crie um arquivo `.env` na raiz do projeto. Você pode copiar o `.env.example` e preencher os valores necessários.

Exemplo de `.env`:
```
# Configurações do TWS (necessárias para modo real)
TWS_HOST=your_tws_host
TWS_PORT=31116
TWS_USER=your_tws_user
TWS_PASSWORD=your_tws_password

# Configurações do LLM (necessárias para IA)
LLM_ENDPOINT=http://localhost:8001/v1 # Ex: Ollama, vLLM
LLM_API_KEY=your_llm_api_key # Pode ser ignorado para alguns LLMs locais
AUDITOR_MODEL_NAME=gpt-4o-mini # Modelo para o IA Auditor

# Modo Mock (para desenvolvimento/testes sem TWS real)
TWS_MOCK_MODE=False # Defina como True para ativar o modo mock

# Perfil de Ambiente (development, production)
APP_ENV=development # Define o perfil de configuração a ser carregado
```

### 4. Executando a Aplicação
Para iniciar o servidor backend:

**Modo Desenvolvimento (com Mock TWS):**
```bash
# Certifique-se que TWS_MOCK_MODE=True e APP_ENV=development no seu .env
uvicorn resync.main:app --reload --host 0.0.0.0 --port 8000
```
A aplicação estará disponível em `http://localhost:8000`.

**Modo Produção (com TWS real):**
```bash
# Certifique-se que TWS_MOCK_MODE=False e APP_ENV=production no seu .env
# E que as variáveis TWS_HOST, TWS_PORT, TWS_USER, TWS_PASSWORD estejam configuradas
uvicorn resync.main:app --host 0.0.0.0 --port 8000
```

### 5. Acessando as Interfaces
*   **Dashboard Principal:** `http://localhost:8000/dashboard`
*   **Chat com IA:** `http://localhost:8000/` (redireciona para o dashboard)
*   **Revisão de Memórias (IA Auditor):** `http://localhost:8000/revisao`
*   **Métricas Prometheus:** `http://localhost:8000/api/metrics`
*   **Documentação da API (Swagger UI):** `http://localhost:8000/docs`

### 6. Executando Testes
Para rodar os testes unitários e a análise estática:
```bash
# Rodar testes unitários
make test

# Rodar linters e type checker
make fmt
```