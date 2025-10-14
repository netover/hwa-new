Refatoração concluída da função call_llm usando o padrão Factory:

1. Criado um novo módulo resync/core/utils/llm_factories.py com:
   - LLMFactory (fábrica principal)
   - LLMProviderFactory (fábrica de provedores)
   - LLMProvider (classe base)
   - OpenAIProvider, OllamaProvider, AnthropicProvider, DefaultLLMProvider (implementações específicas)

2. Refatorada a função call_llm para usar a fábrica:
   - Nova implementação simples: return await LLMFactory.call_llm(...)
   - Removida toda a lógica complexa de tratamento de exceções e configuração

3. Benefícios da refatoração:
   - Complexidade ciclomática reduzida de C (20) para níveis aceitáveis
   - Código mais modular, testável e manutenível
   - Cada fábrica pode ser testada independentemente
   - Novos provedores podem ser adicionados sem modificar o código existente
   - Código mais legível e com responsabilidade única
   - Melhor separação de preocupações
   - Facilita a adição de novos provedores LLM no futuro

4. Alterações no sistema:
   - Arquivo llm.py atualizado para usar a nova fábrica
   - Arquivo llm_factories.py criado com a nova implementação
   - Nenhuma alteração necessária nos códigos que usam a função call_llm

A tarefa foi concluída com sucesso e o plano de refatoração foi atualizado.