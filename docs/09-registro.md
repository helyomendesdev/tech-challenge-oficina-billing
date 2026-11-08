# Registro de trabalho

## 05/11/2026 — Documentação inicial

Solicitação: compreender o existente nos repos do Hélio, delimitar a parte do Lucas e começar
pela documentação para continuidade com outra IA. Lucas confirmou implementação ainda não iniciada.

Realizado:

- Leitura do enunciado e das mensagens técnicas de divisão/andamento da Fase 4.
- Inventário de metadados, branches e PRs abertos de oito repos do grupo.
- Leitura dirigida de 62 arquivos relevantes e atualização de arquivos OS após mudança na main.
- Consulta de código/contratos/workflows e resultados de CI remotos; sem rodar suítes dos serviços.
- Registro dos achados A-01 a A-15, plano PR-01 a PR-10, decisões e dependências.
- Criação de README, AGENTS e nove documentos de continuidade.
- Consulta às fontes oficiais sobre Actions, testes Mercado Pago, variantes Checkout e planos Sonar.

Verificação desta entrega: 11 Markdown, links locais e whitespace conferidos sem erros.
Código dos serviços não foi executado. A tentativa de criar o primeiro README no GitHub
falhou com HTTP 403 (`Resource not accessible by integration`); nenhum commit foi criado.
Publicação alternativa autorizada: Confluence existente, espaço pessoal Lucas Marques,
mais pacote Markdown para futura importação. Criados o hub e dez páginas filhas; índice publicado com links diretos. Hub: [documentação do Lucas](https://marqs.atlassian.net/wiki/spaces/~7120204dc1d32324e343dcad205794dd624c7c/pages/26247169/Tech+Challenge+Fase+4+Lucas+Billing+Mercado+Pago+e+JWT). IDs/URLs das páginas preservados em PUBLICACAO.json.

Não realizado: código Billing, instalação de dependências, migrations, testes funcionais, cobertura,
CI Billing, integração financeira/JWT da Fase 4, BDD real, deploy ou alteração em outros repos.

Sem nova contratação, recurso de nuvem, pagamento, merge, mensagem ao grupo ou upload dos anexos
privados. O repo Billing permanece vazio; não há main criada por esta sessão.

## 05/11/2026 — Repositório temporário autorizado

Lucas autorizou um repo em sua própria conta para continuar o trabalho e migrar depois.
Criado `O-marqs/tech-challenge-oficina-billing-temp`, público, com README inicial,
commit `cf141eb2bc6e41f7782bee638c8f4d1fcb68bbab`. Autenticação foi feita pelo fluxo seguro;
nenhum dado de autenticação foi incluído nos documentos ou no repositório.
Criada por API a branch `docs/fase4-lucas-planejamento`; pacote documental atualizado com
instruções de migração e distinção entre temporário e destino.
O destino do Hélio segue inalterado. Nenhum serviço, workflow ou recurso pago foi criado.
Os HEADs main de OS, Saga, Auth e Execution foram reconfirmados para integração futura.
Estado funcional permanece NÃO INICIADO; nenhuma suíte de Billing foi executada.

Publicação documental confirmada: commit `5b4d88a5570917734fe927673e9424a42a9eddb1`,
13 arquivos (12 Markdown e PUBLICACAO.json), branch `docs/fase4-lucas-planejamento`.
[PR #1 em rascunho](https://github.com/O-marqs/tech-challenge-oficina-billing-temp/pull/1),
sem merge. Árvore remota e leitura de AGENTS.md conferidas após publicação.
Verificação local: links internos e whitespace válidos; nenhuma alegação de teste funcional.

## 05/11/2026 — Implementação acelerada autorizada

Criada branch feat/billing-mvp-local a partir da documentação publicada. Implementados API,
JWT cliente, catálogo, PostgreSQL/SQLite, Alembic, inbox/outbox, SQS FIFO, operações duráveis,
provider fake e adapter de testes Mercado Pago Orders. Primeiro resultado local: 62 PASS,
3 SKIP PostgreSQL e cobertura 96,98%. Demonstração isolada e migrations executadas.
Conferir docs/11-implementacao.md para limitações e resultados posteriores de CI.

### Validação final da implementação funcional

Código validado no commit remoto e7f668df37324c902a0140cc32cea73fb24d7bcf.
Run 42110862161: 73 PASS, 96,92% incluindo CLI, nenhum SKIP; Ruff/formato/Bandit,
Alembic upgrade/check, auditoria de dependências e Docker passaram. Smoke de containers
com API/workers/PostgreSQL/LocalStack completou confirmação fake explícita, estorno e
cancelamento. Nenhuma evidência de integração real MP, stack OS/Execution ou deploy.
PR #2 continua em rascunho, sem merge. Próxima tarefa depende de credenciais de TESTE MP
e dos ajustes de integração já registrados no grupo.

## 05/11/2026 — Revisão adicional e separação das pendências

Reconfirmados os HEADs OS/Auth/Execution. Saga avançou para
3a5c61f7cb1c9625834a17efe4fa748e15d359b0, corrigindo filas por destinatário (A-07).
Execution ainda tem implementação em feat/execution-service, 34fa9a67859f63123e3a51eefa1699026279ec61;
não confundir main inicial com ausência de desenvolvimento na branch.

Corrigido adapter Orders: confirmação exige ID da transação; estorno confere BRL, referência,
total e transação antes da chamada. Reembolso integral usa body vazio conforme a API e exige
refunds processados com IDs únicos, transação e soma integral para emitir PagamentoEstornado.
Resposta incompleta permanece pendente; não cancela orçamento como se tivesse compensado.
MERCADO_PAGO_RETURN_URL agora é enviada em config.online; callback é configurado no painel.

Acrescentadas 20 regressões. Local Python 3.12: 90 PASS, 3 SKIP PostgreSQL, cobertura 97,38%;
Ruff/formato/Bandit, demo e diff check passaram. CI Python 3.11/PostgreSQL 16:
93 PASS, sem SKIP, 97,25%; build Docker, auditoria sem vulnerabilidades conhecidas nos pacotes
consultados, migrations/drift e stack Billing com PostgreSQL/SQS LocalStack passaram.
Commit funcional remoto ebd919fb1826c088c51407d113657ec15f271377,
[run 42120591700](https://github.com/O-marqs/tech-challenge-oficina-billing-temp/actions/runs/42120591700).

Criado docs/12-proximos-passos-e-alinhamentos.md com matriz de responsáveis, perguntas objetivas,
fontes atuais do provedor e roteiro de sandbox. Atualizados plano, causa HTTP e handoff para refletir
o código existente. Sem alteração em repo do grupo, segredo, transação real, merge, deploy ou gasto contratado.

## 05/11/2026 — Migração oficial solicitada pelo Lucas

Destino reconferido vazio; permissão push informada e ensaio de envio aceito pelo Git.
Decidida importação integral do histórico dos dois PRs, preservando commits e autoria.
Ancestralidade do PR #1 no HEAD do PR #2 e integridade do clone verificadas.
Publicação via bootstrap original, branch feat/migracao-billing e PR com CI antes do merge.
Somente documentação de localização/continuidade foi ajustada nesta etapa.
Fonte: [registro de migração](13-migracao-oficial.md). Nenhum deploy foi solicitado.

## 08/11/2026 — Sonar, CD e preparação do sandbox

A base oficial foi conferida no commit `2e5352541310f68346ffd8a4e1df4da845b7cc91`.
O [CI do Billing](https://github.com/helyomendesdev/tech-challenge-oficina-billing/actions/runs/42255567826)
mostra 95 testes e 97,07% de cobertura. O PR #2 de New Relic já foi integrado.

O OS já inclui payloads completos e login de funcionário. O driver da Saga usa dois tokens
e chama a CLI de pagamento fake do Billing. Os PRs OS #25 e Saga #8 ainda estavam abertos
na conferência. O Execution já serializa Decimal em sua branch e ainda precisa expor o
comando de conclusão e falha para o BDD. A branch `feat/shared-infrastructure` do repo k8s
define os ECRs dos serviços e as filas SQS.

A preparação inclui análise Sonar com relatório de cobertura, workflow CD manual para
homologação, imagem por digest, Job de migração por tentativa e rollout após migração.
O Compose sandbox separa o banco e as filas do ambiente fake e carrega as chaves de
um arquivo local protegido. Os passos e parâmetros estão no [README](../README.md).

Validação local com Python 3.12.14:
- Ruff, formato, Bandit, `uv lock --check --offline` e `git diff --check` passaram.
- 92 testes passaram com 97,07% de cobertura. Três testes de PostgreSQL exigem banco de teste.
- A demo fake passou. YAML, scripts Bash e cobertura relativa foram validados.
- Com comandos simulados, o CD bloqueou CI ausente e falha de migração. A sequência de
  publicação e rollout passou na simulação. A configuração Sonar foi validada para
  ausência, preenchimento parcial e preenchimento completo.
- Sonar remoto, deploy no cluster e compra de teste no provedor aguardam configuração.

Na preparação do patch, a criação da branch via integração GitHub recebeu HTTP 403. As mudanças ficaram na branch
local `feat/billing-entrega-k8s-sonar`, base com árvore idêntica à main oficial conferida,
e em um patch para aplicar e publicar pelo acesso Git do Lucas.


### Aplicação no Billing oficial

O patch passou em `git apply --check` e foi aplicado com `git apply --index` na
branch `feat/billing-entrega-k8s-sonar`, criada a partir de `origin/main` em `2e53525`.
O CD agora exige CI bem-sucedido na própria `main` e define `KUBECONFIG` na etapa
de configuração. Os workers preservam o entrypoint da imagem para carregar o agente
New Relic quando houver licença.

- Python 3.11.9: Ruff, formato, Bandit, auditoria de dependências, lockfile e build do wheel passaram.
- Pytest local: 92 passaram, 3 de PostgreSQL ficaram para o CI e a cobertura foi de 97,07%.
- `actionlint`, sintaxe Bash, caminhos de cobertura, simulações de Sonar/CD e configuração
  dos dois projetos Compose passaram. O sandbox foi renderizado com valores fictícios.
- A demo fake completou o fluxo no Windows e saiu com erro ao limpar o SQLite temporário.
  PostgreSQL e o fluxo entre containers são verificados no CI. Sonar Cloud, homologação
  no EKS e transações de teste no provedor dependem da configuração descrita no README.
