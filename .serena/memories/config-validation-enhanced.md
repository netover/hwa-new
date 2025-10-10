Aprimorei a validação de configuração no settings.py adicionando:
- Validador para formato da URL Redis (deve começar com 'redis://')
- Validador de força mínima da senha do admin (mínimo 8 caracteres)
- Mantive todas as validações Pydantic existentes
- As validações funcionam corretamente conforme testado