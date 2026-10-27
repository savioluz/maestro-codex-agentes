# MAESTRO — Instruções do repositório para Codex (VS Code e CLI)

Este repositório é um **kit de configuração do Codex**, não um SaaS executável. Use Português do Brasil. Leia apenas os arquivos pertinentes à tarefa; mantenha respostas verificáveis.

## Ativação e mapa

- Maestro (agente principal): use a skill `$maestro`, armazenada em `.agents/skills/maestro/SKILL.md`, e a referência `.agents/orchestrator/MAESTRO.md`.
- Dez **subagentes reais do Codex** estão declarados em `.codex/agents/*.toml`: `django_mysql`, `nextjs_frontend`, `apps_games`, `qa_testing`, `guardian_security`, `vps_nodocker`, `marketing_pitch`, `docs_reports`, `skills_guardian`, `cloud_deploy`.
- Skills especializadas e fluxos migrados estão em `.agents/skills/<nome>/SKILL.md`. No Codex são acionados por `$nome` ou selecionados quando a descrição se aplica; não confunda com comandos `/<nome>` do Antigravity.
- Workflows originais adaptados: `.agents/workflows/`; registro de estado: `.agents/PROJECT_STATE.md`.
- Modelos reutilizáveis: `templates/` (landing page, Nginx, PM2, Systemd, MySQL, segurança).

## Roteamento

| Demanda | Agentes / skills |
| --- | --- |
| SaaS Django + MySQL | `django_mysql` / `django-mysql-saas`, `$novo-saas` |
| Next.js / landing page / SEO | `nextjs_frontend` / `premium-ui-system`, `nextjs-seo-master`, `$nova-landing-page` |
| Jogo/PWA | `apps_games` / `game-canvas-pwa` |
| Testes | `qa_testing` / `qa-automated-testing` |
| Segurança | `guardian_security` / `security-seal-audit`, `$auditoria-seguranca` |
| Cloud, GitHub e deploy MERCADO3D | `cloud_deploy` / `$deploy-mercado3d` |
| VPS sem Docker | `vps_nodocker` / `vps-nodocker-deploy`, `$deploy-vps` |
| Marketing / pitch | `marketing_pitch` / `marketing-pitch-showcase`, `$apresentacao-pitch` |
| Documentação e orçamento | `docs_reports` / `docs-reports-pro`, `$novo-documento-orcamento` |
| Erros recorrentes e manutenção das skills | `skills_guardian` / `$skills-guardian` |

## Alertas de falhas e melhoria das skills

- Contato responsável GitHub: `@savioluz`; e-mail de alertas: `savioluz.dev@gmail.com`.
- Se uma ferramenta terminar com erro não-zero, registre os sintomas mínimos, associe a receita de `.agents/knowledge/ERROR_CATALOG.json`, recomende correção e teste. A integração automática opera por `.codex/hooks.json` e scripts do kit após aprovação do hook e configuração SMTP, mas pode não observar erros internos do host.
- O curador `skills_guardian` revisa `.maestro/knowledge/SKILLS_REVIEW_QUEUE.md` (arquivo local ignorado pelo Git). Hipóteses não devem ser promovidas a verdade sem reproduzir a falha e validar um teste.
- Não altere `.env` alheio, não exponha senha de app e não se comunique por WhatsApp/API de mensageria. Use somente e-mail SMTP configurado pelo proprietário.
- Não altere identidade Git global, credenciais, remotes nem publique para @savioluz sem pedido explícito.

## Protocolo de execução

1. Inspecione arquivos e dependências. Para trabalho amplo, defina plano curto e critérios de aceite.
2. Invoque skills e subagentes *somente* quando necessários. Paralelize tarefas independentes; nunca permita edições concorrentes no mesmo arquivo sem coordenação.
3. Preserve convenções, teste mudanças relevantes e mostre resultados de comandos realmente executados. Nunca declare cobertura, performance, ranking de SEO ou proteção OWASP sem evidência.
4. A checagem `templates/security/audit_seal.py` é uma **varredura heurística** e não certifica conformidade nem substitui pentest, revisão humana ou dependency scanning.
5. **Não** faça deploy, SSH, sudo, exclusões, migrações irreversíveis ou operações em produção sem solicitação e autorização explícita. Nunca exponha credenciais. Valide placeholders dos templates antes de usá-los.
6. Quando o pedido for só conteúdo, planejamento ou código local, não crie infra, serviço externo ou artefatos adicionais sem necessidade.
7. Informe o que foi feito, quais arquivos mudaram, testes executados ou não executados, riscos e próximos passos.

## Validação do kit

Rode `python scripts/validate_codex_project.py`. Verificações de sintaxe e integridade não equivalem a testar execução real no Codex autenticado.

Veja `README.md` e `GUIA_PREMIUM_ECOSSISTEMA.md` para instalação e uso.
