# Otimização e Melhoria Contínua - Resync

Este documento descreve o plano para implementar as otimizações identificadas no projeto.

## 1. Implementação de Injeção de Dependências (Concluído)

-   **Objetivo:** Eliminar o padrão Singleton global e implementar um sistema de injeção de dependências.
-   **Ação:** Criar um container de DI e refatorar os componentes principais para usar injeção de dependências.
-   **Passos:**
    1.  ✅ Criar módulo `resync/core/di_container.py` com implementação do container DI.
    2.  ✅ Definir interfaces para os componentes principais em `resync/core/interfaces.py`.
    3.  ✅ Refatorar `AgentManager`, `ConnectionManager`, `AsyncKnowledgeGraph` e `AsyncAuditQueue` para usar DI.
    4.  ✅ Integrar o container DI com o sistema de dependências do FastAPI.
    5.  ✅ Atualizar endpoints para usar injeção de dependências.
    6.  ✅ Criar testes unitários para o container DI e exemplos de uso em testes.
    7.  ✅ Documentar o padrão de DI implementado.

## 2. Tratamento de Erros no Cliente TWS (Alta Prioridade)

-   **Objetivo:** Aumentar a robustez da comunicação com a API do TWS, tratando erros transientes de rede.
-   **Ação:** Implementar um mecanismo de retentativas (retry) com backoff exponencial no `OptimizedTWSClient`.
-   **Ferramenta:** Utilizar a biblioteca `tenacity`.
-   **Passos:**
    1.  Adicionar `tenacity` ao `requirements.txt`.
    2.  Aplicar o decorador `@retry` da `tenacity` ao método `_api_request` em `resync/services/tws_service.py`.
    3.  Configurar o `retry` para tratar exceções de conexão (ex: `httpx.RequestError`) e aguardar um tempo crescente entre as tentativas.
    4.  Criar/ajustar testes para validar o comportamento de retry.

## 3. Otimização de Locks no Cache (Média Prioridade)

-   **Objetivo:** Reduzir a contenção e melhorar a performance do cache em cenários de alta concorrência.
-   **Ação:** Substituir o lock único por um mecanismo de locks particionados (sharded locks) nas classes `AsyncTTLCache` and `L1Cache`.
-   **Passos:**
    1.  Modificar as classes de cache para manter uma lista de locks.
    2.  Implementar uma função de hash para mapear uma chave de cache a um lock específico.
    3.  Atualizar os métodos `get`, `set`, `delete` para usar o lock particionado correto.
    4.  Analisar o impacto na complexidade e na performance.

## 4. Evolução do Cache Hierárquico (Baixa Prioridade)

-   **Objetivo:** Melhorar a eficiência do cache.
-   **Ação:** Pesquisar e potencialmente implementar algoritmos de evicção mais avançados (ex: LFU, ARC) ou uma política de write-back.
-   **Passos:**
    1.  Analisar os padrões de acesso ao cache na aplicação.
    2.  Comparar o desempenho dos algoritmos alternativos com o LRU atual.
    3.  Implementar a política de cache escolhida se o ganho de performance justificar a complexidade adicional.

## 5. Inicialização Paralela (A ser considerado no futuro)

-   **Objetivo:** Acelerar o tempo de inicialização da aplicação.
-   **Ação:** Identificar componentes independentes que possam ser inicializados em paralelo.
-   **Status:** Atualmente, o lazy loading já oferece uma boa performance. Esta é uma otimização a ser considerada conforme o sistema cresce.