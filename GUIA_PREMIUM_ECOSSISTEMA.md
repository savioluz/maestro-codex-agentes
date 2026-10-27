# Guia do Maestro no VS Code com Codex

**Versão adaptada para Codex • 26/10/2026**

## Visão geral

O kit transforma um conjunto de prompts, skills e fluxos do Antigravity em um repositório que o Codex pode ler e usar no Visual Studio Code. O Maestro é a orquestração da conversa principal (skill `$maestro`), e os dez especialistas são agentes TOML autênticos. O Codex decide quando delegar atividades, conforme a configuração e os recursos disponíveis.

## Instalação rápida

1. Extraia o ZIP e abra a pasta no VS Code.
2. Instale a extensão Codex da OpenAI (identificador `openai.chatgpt`); faça login.
3. Abra a barra lateral com `Codex: Open Codex Sidebar`.
4. Confie no projeto, se solicitado: as opções em `.codex/config.toml` dependem disso.
5. Envie `$maestro — explique a arquitetura do kit e proponha um primeiro projeto.`

Para uso em projetos externos, execute `bash install.sh --global` ou `./install.ps1 -Global` e depois abra o projeto desejado. Instalação global não modifica seu `config.toml` pessoal.

## Organização

| Arquivo | Função |
| --- | --- |
| `AGENTS.md` | Padrões e decisões gerais do Codex no repositório |
| `.codex/config.toml` | Ativa subagentes e limita a concorrência a 4 |
| `.codex/agents/*.toml` | Define 10 papéis especializados reais |
| `.agents/skills/*/SKILL.md` | Metadados de roteamento e procedimentos das skills |
| `.agents/orchestrator/MAESTRO.md` | Plano operativo detalhado do Maestro |
| `.agents/workflows/` | Guias originais adaptados |
| `templates/` | Arquivos de exemplo para Next.js, Nginx, MySQL, PM2, Systemd e auditoria |

## Agentes e habilidades

1. `django_mysql`: Django, APIs, MySQL e multi-tenancy; `$django-mysql-saas`.
2. `nextjs_frontend`: React/Next.js, UX e SEO; `$premium-ui-system`, `$nextjs-seo-master`.
3. `apps_games`: Canvas/WebGL/PWAs; `$game-canvas-pwa`.
4. `qa_testing`: Pytest/Vitest/Playwright; `$qa-automated-testing`.
5. `guardian_security`: autenticação, segredos e revisão OWASP; `$security-seal-audit`.
6. `vps_nodocker`: Nginx/Gunicorn/Systemd/PM2/MySQL; `$vps-nodocker-deploy`.
7. `marketing_pitch`: decks, demos, propostas executivas; `$marketing-pitch-showcase`.
8. `docs_reports`: orçamentos, especificações e documentação; `$docs-reports-pro`.
9. `skills_guardian`: detecção, diagnóstico, propostas de correção e evolução das skills; `$skills-guardian`.
10. `cloud_deploy`: preparação de produção, diagnóstico e deploy assistido cloud; `$deploy-mercado3d`.

**Nota:** agente especializado é diferente de skill. A skill é documentação executável sob demanda; o subagente tem uma conversa própria quando o Codex permite a delegação. Nenhuma skill, por si só, executa comandos do sistema sem o Codex decidir e obter as permissões necessárias.

## Fluxos migrados

| Comando que se digitava no Antigravity | No chat do Codex |
| --- | --- |
| `/maestro` | `$maestro` |
| `/maestro-orchestrator` | `$maestro-orchestrator` |
| `/novo-saas` | `$novo-saas` |
| `/nova-landing-page` | `$nova-landing-page` |
| `/auditoria-seguranca` | `$auditoria-seguranca` |
| `/auditoria-seo` | `$auditoria-seo` |
| `/deploy-vps` | `$deploy-vps` |
| `/apresentacao-pitch` | `$apresentacao-pitch` |
| `/novo-documento-orcamento` | `$novo-documento-orcamento` |

Para descobrir skills, digite `$` no compositor ou execute `/skills` quando disponível. Uma tarefa bem descrita também pode ativar a skill implicitamente.

## Prompts prontos

**Novo SaaS:**

> Use $novo-saas. Crie um plano e implemente, numa pasta nova, uma aplicação de gestão comercial com Django, MySQL e Next.js. Entregue instruções de instalação, testes automatizados e política de isolamento entre organizações. Sem deploy.

**Landig page:**

> Use $nova-landing-page para produzir uma página responsiva e acessível de um SaaS. Escolha um visual adequado ao produto, implemente metadados e um checklist verificável de SEO e performance.

**Auditoria:**

> Use $auditoria-seguranca, leia este repositório e apresente achados priorizados com arquivo/linha, risco e sugestões de correção. Não modifique produção. Diferencie checagens realizadas das não realizadas.

**VPS:**

> Use $deploy-vps para preparar os arquivos de deploy para Ubuntu 24.04 sem Docker. Não execute comandos remotos, não configure serviços de produção e valide todos os placeholders que exigem valores meus.

**Apresentação:**

> Use $apresentacao-pitch para preparar uma apresentação executiva de uma plataforma de pedidos, com público-alvo, problema, solução, diferenciais, custos estimados e roteiro de demo.

## Garantias e verificação

A validação estrutural `python scripts/validate_codex_project.py` confirma a presença e o formato esperado dos arquivos — não substitui teste real da extensão. O script legado `templates/security/audit_seal.py` encontra alguns padrões arriscados em código-fonte, mas **não emite certificação** de segurança ou conformidade OWASP. O sucesso em testes deve ser verificado em cada aplicação criada. O kit não cria automaticamente ambiente de execução de aplicações SaaS.

## Documentação histórica

O material original gerado para Antigravity permanece em `docs/legado-antigravity/`, inclusive o PDF legado. O manual **que deve ser seguido** para usar este ZIP é este guia e o `README.md` adaptado.

## Links oficiais

- https://learn.chatgpt.com/docs/ide
- https://learn.chatgpt.com/docs/build-skills
- https://learn.chatgpt.com/docs/agent-configuration/subagents
- https://learn.chatgpt.com/docs/config-file/config-basic


---

## Atualizacao outubro/2026: sistema de alertas + curadoria de skills

O Maestro agora tem **10 agentes** (incluindo `skills_guardian`) e **20 skills**, com um catalogo inicial de **12 erros comuns** e estrategias candidatas de reparo. Quando um hook `PostToolUse` observa erro em ferramenta, a fila local `.maestro/knowledge/SKILLS_REVIEW_QUEUE.md` recebe uma recomendacao de diagnostico e de verificacao. O sistema registra **hipoteses**, nao edita automaticamente instrucoes oficiais das skills sem comprovacao de teste.

**E-mail de alertas**: `savioluz.dev@gmail.com`. Para enviar de verdade, configure senha de app do Gmail em `python scripts/setup_email.py`, teste com `python scripts/alert_email.py --test` e libere os hooks de projeto no Codex. Alertas cobrem tarefas monitoradas, erros observaveis por hooks e validacao CI com secret `MAESTRO_SMTP_PASSWORD`. Nenhum sistema de WhatsApp compoe essa versao.

**GitHub do responsavel**: `@savioluz`. Configure com `git init` e `python scripts/git_savioluz.py`; depois, se desejar criar um repo privado, autentique a GitHub CLI e execute `gh repo create savioluz/maestro-codex-vscode --private --source . --remote origin --push`. O Codex nao executa publicacao automaticamente.

Guia tecnico atualizado em `docs/ALERTAS_E_SKILLS.md` e `docs/GIT_SAVIOLUZ.md`.
