# Migração para o repositório oficial

Data: 05/11/2026. Lucas solicitou transferir integralmente os PRs
[#1](https://github.com/O-marqs/tech-challenge-oficina-billing-temp/pull/1) e
[#2](https://github.com/O-marqs/tech-challenge-oficina-billing-temp/pull/2)
para `helyomendesdev/tech-challenge-oficina-billing`, incluindo a integração na main.

## Escolha e verificações antes da publicação

- Destino consultado pelo conector e por `git ls-remote`: vazio, sem branches ou commits.
- A conexão informa permissão de escrita; o Git local aceitou o ensaio de push.
- Importar o histórico completo, preservando SHAs e autoria, sem force push.
- O HEAD documental `6620a53a8d4c745ad9a06189a8fb897ca9111a97` é ancestral do
  HEAD funcional/documental `e65bd1808997b97ca5ef4162690ed13db1a428a1`.
  Assim, a branch do PR #2 contém integralmente a sequência dos dois PRs.
- `git fsck --full` passou no clone usado para transporte.
- Usar o commit inicial original `cf141eb2bc6e41f7782bee638c8f4d1fcb68bbab`
  como bootstrap da main e publicar a sequência em `feat/migracao-billing`.
- Abrir PR no destino e executar CI antes de integrar, mantendo os commits originais.
  A solicitação atual do Lucas autoriza esta migração e integração; não autoriza deploy.
- O único workflow contém testes, auditoria, build e containers locais. Não há job de deploy.

## Referência atual

Continuar no [Billing oficial](https://github.com/helyomendesdev/tech-challenge-oficina-billing).
Durante a validação da migração, usar `feat/migracao-billing`; após sua integração, usar main.
Consultar o PR e o Actions do destino para o estado da publicação, checks e merge.
Os documentos anteriores e as URLs do temporário são evidências históricas de origem.
O temporário e seus PRs serão preservados.

O transporte não altera código de negócio, contratos, dependências ou configurações
de infraestrutura. Credenciais, configurações externas e permissões do temporário não migram.
Continuam pendentes Mercado Pago autenticado em teste, integração OS/Execution/BDD,
identidade atendente, spans e CD/K8s conforme docs/12-proximos-passos-e-alinhamentos.md.
