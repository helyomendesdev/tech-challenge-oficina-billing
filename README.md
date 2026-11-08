# Oficina Billing — Fase 4

Implementação inicial do participante Billing no repositório oficial
`helyomendesdev/tech-challenge-oficina-billing`.
Os PRs #1 e #2 do temporário foram reunidos em `feat/migracao-billing` para validação
e integração na main. Consulte o [registro de migração](docs/13-migracao-oficial.md).

## O que já funciona

- Gerar/cancelar orçamento, aprovar/recusar via API, validade e preços snapshot em centavos.
- JWT RS256 com claims do Auth e isolamento por cliente; Swagger em `/docs`.
- PostgreSQL/SQLAlchemy, migrations Alembic, inbox idempotente e outbox transacional.
- Consumer/publisher SQS FIFO e relay; correlação `sagaId`/`requestId` e atributos W3C.
- Intenções de checkout/estorno persistidas, retry com chave estável e reconciliação por CLI.
- Provedor fake explícito para demonstração e adapter Mercado Pago Checkout Pro Orders,
  coberto por HTTP mocks. Checkout criado nunca confirma pagamento automaticamente.
- Agente New Relic na API e nos workers. O teste relatado no PR percorreu a abertura
  da OS até `IniciarExecucao` no mesmo trace. [PR #2](https://github.com/helyomendesdev/tech-challenge-oficina-billing/pull/2)

O sandbox do Mercado Pago e a conclusão da Saga com Execution ainda precisam de
evidência. O atendente faz login no OS. As operações de orçamento no Billing usam o
token do cliente dono.

## Experimente em um comando depois de instalar

Requer Python 3.11 e [uv](https://docs.astral.sh/uv/getting-started/installation/).

```bash
uv sync --frozen --extra dev
uv run python scripts/demo.py
```

A demonstração cria banco SQLite temporário com Alembic, gera JWT efêmero, chama a aprovação
HTTP e percorre orçamento → pagamento fake explícito → estorno → cancelamento. Imprime
resumo PASS e tipos de eventos; não imprime tokens e não faz transações financeiras.

## Rodar a API localmente

```bash
uv run python scripts/dev_keys.py
uv run billing migrate
```

Linux/macOS:

```bash
export AUTH_JWT_PUBLIC_KEY_B64="$(cat .local/jwt-public.b64)"
uv run uvicorn billing_service.api:app --host 127.0.0.1 --port 8001
```

PowerShell:

```powershell
$env:AUTH_JWT_PUBLIC_KEY_B64 = Get-Content .local/jwt-public.b64 -Raw
uv run uvicorn billing_service.api:app --host 127.0.0.1 --port 8001
```

Abra `http://localhost:8001/docs`. O token de desenvolvimento do cliente 7 fica em
`.local/client-token.txt`, expira em 15 minutos e não deve ser versionado. O script
recria as chaves; reinicie a API com a nova chave pública se executá-lo de novo.
Para a autenticação real do grupo, configure a chave pública do `-auth` em vez dessas chaves locais.

Em outro terminal, crie um orçamento de demonstração:

```bash
uv run billing handle-file --file config/gerar-orcamento.demo.json
```

O `orcamentoId` pode ser encontrado na outbox do banco ou calculado com
`billing_service.contract.stable_id("quote:291be3b9-8b0d-583e-94c1-f9d2ae911fb3")`.
O endpoint POST de aprovação responde 202. Consultas e decisões sem JWT retornam 401;
cliente que não é dono recebe 403. Não há endpoint HTTP de confirmação fake.

## Processos e infraestrutura local

`compose.yml` sobe PostgreSQL exclusivo, LocalStack SQS, migrations, criação das filas,
API na porta 8001 e três workers. Provedor **fake**, apenas desenvolvimento.

```bash
docker compose up --build
```

É preciso fornecer `AUTH_JWT_PUBLIC_KEY_B64` para usar as rotas de negócio.
Os três processos separados da mesma imagem são:

```bash
uv run billing consume
uv run billing operations
uv run billing relay
```

Para validar a comunicação entre os containers após subir a stack, execute
`uv run python scripts/smoke_stack.py`. Isso usa confirmação fake explícita via CLI;
não é teste do Mercado Pago nem da stack completa do grupo.

As URLs SQS vêm de `QUEUE_BILLING_COMANDOS_URL` e `QUEUE_OS_SAGA_RESPOSTAS_URL`.
Ack só ocorre após commit de estado/inbox/intenção/outbox. Falha na publicação mantém a
outbox; reenvio usa o mesmo messageId. A janela de dedupe SQS não substitui a inbox.
Outbox mantém ordem por Saga mesmo com mais de um relay PostgreSQL.

## Verificação

```bash
uv run ruff check .
uv run ruff format --check .
uv run bandit -q -r billing_service
uv run pytest --cov=billing_service --cov-report=term-missing --cov-report=xml
uv run alembic check
uv build --wheel
```

O commit oficial `2e53525` passou com 95 testes e 97,07% de cobertura, incluindo PostgreSQL
e o fluxo entre containers. [Evidência do CI](https://github.com/helyomendesdev/tech-challenge-oficina-billing/actions/runs/42255567826)
Para testar locking/transações reais, use um **banco de teste descartável** em
`TEST_DATABASE_URL`; a fixture recria as tabelas desse banco. O CI fornece PostgreSQL 16.
Não aponte testes para um banco com dados reais.

## SonarQube Cloud

Cadastre um projeto com análise pelo CI. No GitHub, configure as variáveis
`SONAR_ORGANIZATION` e `SONAR_PROJECT_KEY` e o secret `SONAR_TOKEN`.
O job `tests` usa `coverage.xml` e aguarda o Quality Gate na main e em PRs do próprio
repositório. Se os três valores estiverem ausentes, o job informa que a análise ainda
aguarda configuração. Configuração parcial falha com o nome do item faltante.

## Deploy de homologação no Kubernetes

Execute **Billing CD** pelo Actions na `main` quando o ambiente estiver pronto. O workflow
manual exige sucesso do Billing CI na `main` para o commit selecionado. Ele publica a imagem no ECR,
usa o digest retornado, executa um Job de migração por tentativa e aguarda os rollouts
da API e dos workers.

| Local | Configuração |
|---|---|
| Variáveis do repositório no GitHub | `AWS_REGION`, `EKS_CLUSTER_NAME` e `ECR_REPOSITORY` se diferente de `oficina-billing`. O runner precisa de acesso à API do cluster e de AWS CLI, Docker, `gh` e `kubectl` compatível. Use `BILLING_DEPLOY_RUNNER` se o grupo precisar indicar um runner. |
| Secrets do environment | `AWS_ROLE_ARN` para OIDC ou `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY` e `AWS_SESSION_TOKEN` temporários do Learner Lab. |
| Namespace `oficina-billing` | ServiceAccount `billing-runtime` com acesso às filas. O deploy usa ConfigMap `billing-config` e Secret `billing-secrets` existentes. |
| ConfigMap `billing-config` | `APP_ENV=test`, `PAYMENT_PROVIDER`, `AWS_REGION`, `AUTH_JWT_PUBLIC_KEY_B64` e as duas URLs FIFO do Billing. |
| Secret `billing-secrets` | `DATABASE_URL` do PostgreSQL com dialeto `postgresql+psycopg`. Para os testes do Mercado Pago, acrescente as credenciais do provedor e configure as URLs HTTPS. Para tracing, forneça `NEW_RELIC_LICENSE_KEY`. |

A infraestrutura do grupo fornece cluster, ECR, banco e filas. Preserve a compatibilidade
das migrations com os pods que ainda estiverem em execução durante a atualização.

## Sandbox do Mercado Pago

Depois de gerar a chave pública de desenvolvimento e preparar o endereço HTTPS, preencha
`.env.sandbox` com `AUTH_JWT_PUBLIC_KEY_B64`, `MERCADO_PAGO_ACCESS_TOKEN`,
`MERCADO_PAGO_WEBHOOK_SECRET`, `MERCADO_PAGO_NOTIFICATION_URL` e `MERCADO_PAGO_RETURN_URL`.
Cadastre o webhook de teste em `/api/v1/webhooks/mercado-pago` no painel do provedor.

```bash
docker compose -p oficina-billing-sandbox --env-file .env.sandbox -f compose.yml -f compose.sandbox.override.yml config --quiet
docker compose -p oficina-billing-sandbox --env-file .env.sandbox -f compose.yml -f compose.sandbox.override.yml up -d --build --wait
```

O projeto Compose separado isola banco e filas da demonstração fake. Os dois usam as
portas 8001 e 4566 do host, então execute um ambiente por vez. Siga os cenários de pagamento,
recusa e estorno no [roteiro de sandbox](docs/12-proximos-passos-e-alinhamentos.md).

## Integração e limites atuais

Os 14 schemas Billing estão fixados no commit `ed3a8345ba684fc442193084ed7b8cbf72c3cdb9`
do `-saga`, sem alterações ([proveniência](billing_service/contracts/SOURCE.md)).
O contrato HTTP de aprovação é mantido. O total é calculado por catálogo próprio configurável;
`config/catalog.demo.json` contém exclusivamente preços sintéticos. Totais zero são rejeitados
com OrcamentoFalhou; isso evita inventar uma cobrança inválida no contrato de pagamento.

O adapter Mercado Pago usa Orders API, endpoint fixo oficial, chave idempotente e valores Decimal.
Só aceita respostas de orders de teste (`ORDTST...`). Configure a aplicação/conta no modo de teste;
o nome do adapter não transforma uma credencial produtiva em credencial de teste. Webhooks
exigem assinatura, conferência do recurso e consulta autenticada ao provedor. A ativação exige
credenciais e URLs HTTPS em `.env.example`; não foi ativada nesta sessão.

Ainda precisam de evidência o sandbox Mercado Pago, os cenários de conclusão e compensação
do BDD, o Quality Gate no projeto Sonar e o deploy no EKS. Pagamento tardio gera erro explícito
para intervenção.

Para revisar a entrega, ver [o que falta e quem resolve](docs/12-proximos-passos-e-alinhamentos.md).
O documento inclui as perguntas ao grupo e o roteiro de sandbox Mercado Pago. Webhook é
cadastrado no painel Teste; a URL de retorno é enviada em config.online da order. Reembolso
integral exige evidência processada com a transação e o valor esperados, antes do evento da Saga.

Leia [AGENTS.md](AGENTS.md), [continuidade](docs/08-continuidade.md),
[decisões](docs/07-decisoes-pendencias.md), [contratos](docs/04-contratos-integracao.md),
[auditoria do grupo](docs/01-auditoria.md) e [migração](docs/10-migracao-github.md).
