# Prompts de Few-Shot para o Agente TWS

Este arquivo contém exemplos de interações (prompts e respostas ideais) para treinar ou guiar o agente de IA no contexto do HCL Workload Automation (TWS).

---

## Exemplo 1: Status de um Job Específico

**Usuário:** "Qual o status do job `JOB_FINAL_PAYROLL`?"

**Ação do Agente (pensamento):** O usuário está perguntando sobre o status de um job. Devo usar a ferramenta `tws_readonly` com a operação `get_job_status` e os argumentos `job_name="JOB_FINAL_PAYROLL"`.

**Resposta do Agente:** "O job `JOB_FINAL_PAYROLL` foi concluído com sucesso (SUCC) na estação de trabalho `MASTER_CPU`."

---

## Exemplo 2: Jobs em Execução

**Usuário:** "Me mostre os jobs que estão rodando agora."

**Ação do Agente (pensamento):** O usuário quer uma lista de jobs com status 'EXEC' ou 'RUNNING'. Devo usar a ferramenta `tws_readonly` com a operação `search_jobs` e o filtro `status="EXEC"`.

**Resposta do Agente:** "Atualmente, há 2 jobs em execução: `JOB_DATA_LOAD` na estação `AGENT_1` e `JOB_REPORT_GEN` na `AGENT_2`."

---
