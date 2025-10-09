# Plano de Refatoração do Sistema de Cache
## Objetivo
Quebrar a classe AsyncTTLCache monolítica em componentes menores com responsabilidades bem definidas.

## Estrutura Alvo
1. **CacheStorage** - Responsável apenas por armazenamento
2. **CacheTTLManager** - Gerencia expiração de itens  
3. **CacheMetricsCollector** - Coleta e expõe métricas
4. **AsyncTTLCache** - Orquestra os componentes

## Benefícios Esperados
- Maior testabilidade
- Melhor manutenção
- Separação clara de responsabilidades
- Facilita extensão futura
- Redução de complexidade ciclomática