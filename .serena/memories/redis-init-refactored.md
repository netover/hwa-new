Refatorei com sucesso a inicialização do Redis:
- Implementei redis_connection_manager com tratamento granular de erros
- Refatorei initialize_redis_with_retry com retry exponencial e mensagens detalhadas
- Substitui RedisStartupError pelas novas exceções específicas
- Adicionei tratamento para ResponseError, BusyLoadingError e outros casos específicos
- Mantive compatibilidade com a estrutura existente