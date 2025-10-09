# Auditoria Técnica: Núcleo de Cache - Integrações

## Integrações Diretas

### Hierarquia de Cache (L1/L2)
- **Componente**: `CacheHierarchy` em `resync/core/cache_hierarchy.py`
- **Fluxo**: Busca L1 (memória) → L2 (`AsyncTTLCache`) → Fonte de dados
- **Sincronização**: Write-through para ambas camadas
- **Criptografia**: Suporte opcional via `enable_encryption`

### Connection Pools
- **Redis Pool**: `RedisConnectionPool` em `resync/core/pools/redis_pool.py`
  - Utilizado indiretamente pelo `AsyncTTLCache` para persistência
  - Configuração via `resync/settings.py` (REDIS_POOL_*)

- **HTTP Pool**: `HTTPConnectionPool` em `resync/core/pools/http_pool.py`
  - Usado por serviços que consomem APIs externas
  - Integração com `AsyncTTLCache` via cache de respostas

### WebSocket
- **Connection Manager**: `ConnectionManager` em `resync/core/connection_manager.py`
  - Usa `AsyncTTLCache` para armazenar estado de conexões
  - Integração com `WebSocketPoolManager` para monitoramento

### Dependency Injection
- **Container**: `resync/core/di_container.py`
  - Registro e resolução de `AsyncTTLCache` como singleton
  - Injeção automática em serviços que requerem cache

## Configurações e Settings

### Parâmetros Principais (resync/settings.py)
```python
# Cache Hierarchy
CACHE_HIERARCHY_L1_MAX_SIZE = 5000
CACHE_HIERARCHY_L2_TTL = 600
CACHE_HIERARCHY_L2_CLEANUP_INTERVAL = 60

# Robust Cache
ROBUST_CACHE_MAX_ITEMS = 100_000
ROBUST_CACHE_MAX_MEMORY_MB = 100
ROBUST_CACHE_ENABLE_WAL = False
```

### Feature Flags
```python
# Migração Gradual
MIGRATION_USE_NEW_CACHE = False  # Usar ImprovedAsyncCache
```

## Integrações com Serviços

### TWS Client
- **Serviço**: `OptimizedTWSClient` em `resync/services/tws_service.py`
- **Uso**: Cache de status de workstations/jobs
- **Configuração**: TTL específico para diferentes tipos de dados

### LLM Services
- **Serviços**: `LLMCostMonitor`, `TWS_LLMOptimizer` em `resync/core/llm_*.py`
- **Uso**: Cache de prompts e respostas para otimização de custos
- **Estratégia**: TTL curto (300s) para respostas, longo (3600s) para prompts

### Health Checks
- **Serviço**: `HealthCheckService` em `resync/core/health_service.py`
- **Uso**: Verificação de funcionalidade do cache
- **Métricas**: Monitoramento de hit_rate, evictions, errors

## Monitoramento e Métricas

### Prometheus
- **Métricas Exportadas**:
  - `resync_cache_hits`
  - `resync_cache_misses` 
  - `resync_cache_evictions`
  - `resync_cache_size`

### Logging
- **Structural Logger**: `resync/core/structured_logger.py`
- **Correlation IDs**: Rastreamento de operações complexas
- **Níveis**: DEBUG para operações, ERROR/WARNING para falhas

## Testes de Integração

### Suites Relevantes
1. **Core Tests**: `tests/core/test_async_cache.py`
   - Testes de integração com `CacheHierarchy`
   - Validação de comportamento em cenários reais

2. **WAL Integration**: `tests/test_wal_integration.py`
   - Testes de persistência e recuperação
   - Validação de integridade de dados

3. **Stress Testing**: `resync/core/stress_testing.py`
   - Testes de carga com múltiplos serviços
   - Simulação de condições de produção

## Recomendações de Integração

### Melhorias de Configuração
1. **Ambientes Específicos**:
   - Criar profiles para development/staging/production
   - Ajustar limites automaticamente por ambiente

2. **Auto-Tuning**:
   - Implementar ajuste dinâmico de TTL baseado em hit_rate
   - Otimizar número de shards conforme carga

### Expansão de Monitoramento
1. **Business Metrics**:
   - Adicionar métricas de negócio (ex: cache savings em $)
   - Correlacionar performance do cache com UX

2. **Distributed Tracing**:
   - Integrar com OpenTelemetry para tracing completo
   - Rastrear impacto de cache misses em latência de APIs

### Documentação de Integração
1. **Guia de Uso**:
   - Exemplos práticos de integração com novos serviços
   - Boas práticas para configuração de TTL

2. **Troubleshooting**:
   - Diagnóstico de problemas comuns de cache
   - Procedimentos de rollback em produção