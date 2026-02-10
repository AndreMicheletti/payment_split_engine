# Cakto Pay Challenge
## Mini Split Engine

Implementação por André Micheletti.

Pull request criado:
[payment_split_engine/pull/1](https://github.com/AndreMicheletti/payment_split_engine/pull/1)

## Perguntas do teste técnico

### Como garantiu precisão e arredondamento.

Eu utilizei o tipo `Decimal` de python por ser o padrão de industria para cálculos financeiros e matemáticos. Ele possui uma segurança de casas decimais embutida, evitando o uso do `float` que pode gerar inconsistências. Utilizei a função `quantize` que faz operação
de arredondamento usando estratégias pré-definidas pela lib.

### Regra de centavos e por quê.

Decidi aplicar a regra de distribuir inicialmente fazendo um arrendondamento "para baixo"
na casa dos centavos, fazendo com que o excesso fique como uma "sobra" no cálculo. Então
utilizando a sobra, aplico a estratégia de distribuição onde cada um recebe o "round" da
sobra, e apenas o último recebe de fato o que faltaria para fechar a conta.
Esse método é mais seguro pois sempre vai deixar para distribuir os últimos poucos centavos
usando a estratégia de "o último leva o que restou" - o restante é distribuido de forma precisa usando o round.

### Estratégia de idempotência.

Decidi criar um "in-memory cache" para guardar as chaves `idempotency-key` e os payloads, assim consigo comparar quando recebo uma chave e um payload igual. Isso é eficaz principalmente levando em consideração que normalmente essa situação pode ocorrer em
"race-conditions".

### Métricas que colocaria em produção (lista curta).

- Latência p95/p99
- Taxa de requests falhando
- Taxa de casos de Idempotency (conflict e payload igual)
- Taxa de erros de cálculo (soma de percents não bate / soma dos splits não bate com `net amount`)
- Disparo de eventos outbox

### Se tivesse mais tempo, o que faria a seguir.

- Melhoraria os casos de teste para as regras de negócio e segurança (installments, regra de centavos, idempotency)
- Implementaria um cache para a idempotencia utilizando Redis
- Colocaria a inserção no ledger em um worker para não travar o request principal
- Utilizaria um sistema de mensageria para enviar os eventos outbox e utilizaria task workers (celery) para processar os eventos

### Uso de IA

Utilizei a IA com recurso de "auto-complete" e suggest next edit para aumentar produtividade, para gerar casos de teste e para escrever "boilerplate" dos models
e serializers. Sempre verificando o código gerado e fazendo as alterações que preciso
manualmente, pensando na arquitetura que eu já queria alcançar antes de dar o prompt.
