# Maestro — Ecossistema de Agentes para Codex no VS Code

Adaptação do **Antigravity Fullstack Maestro** para o **OpenAI Codex** na extensão do **Visual Studio Code** e na CLI. Inclui um Maestro coordenador, 10 especialistas, 9 skills técnicas originais, 8 fluxos migrados e o alias `$maestro-orchestrator`, templates de infraestrutura, instaladores opcionais e validação estrutural.

> **Importante**: este repositório é um **kit de instruções, agentes, habilidades e templates** — não traz backend/frontend completo em execução. A delegação depende da versão, das permissões e do suporte a subagentes do seu Codex.


## NOVO — Alertas por e-mail, GitHub @savioluz e Skills Guardian

- **Destino:** `savioluz.dev@gmail.com`. Alertas por SMTP do Gmail para erros observados pelos hooks do Codex, tarefas protegidas do VS Code e falhas da validação no GitHub Actions.
- **Configuração indispensável:** rode `python scripts/setup_email.py` e informe sua **senha de app** do Gmail sem digitá-la no chat. Depois execute `python scripts/alert_email.py --test` e confirme o recebimento.
- **Codex:** revise e aprove o hook do projeto em `/hooks` quando solicitado; a extensão/CLI deve respeitar o suporte da versão utilizada. Erros fora das ferramentas observadas não são detectáveis universalmente.
- **Aprendizado automático:** o novo subagente `skills_guardian` e a skill `$skills-guardian` usam 12 receitas iniciais. Falhas monitoradas geram **hipóteses de solução** e fila de revisão; skills permanentes só mudam após confirmação e testes.
- **GitHub:** `@savioluz` no CODEOWNERS. Configure o secret `MAESTRO_SMTP_PASSWORD` no seu repositório GitHub para os alertas de CI. Para inicializar o Git, rode `git init` e `python scripts/git_savioluz.py`.
- **Mensageria:** nenhuma API ou sistema de WhatsApp integra este kit; removemos as referências de compartilhamento por WhatsApp das skills e agentes ativos de marketing.

Guia completo: **[Alertas + Skills Guardian](docs/ALERTAS_E_SKILLS.md)** · **[Comandos Git @savioluz](docs/GIT_SAVIOLUZ.md)**.

## 1. Como começar (sem instalar nada globalmente)

1. Extraia este ZIP e abra a pasta `Maestro-Codex-VSCode` usando **Arquivo > Abrir Pasta** no VS Code.
2. Instale a extensão oficial **Codex — OpenAI** (ID da extensão: `openai.chatgpt`) e faça login com a sua conta disponível.
3. Abra **Codex: Open Codex Sidebar** pela paleta de comandos se a barra lateral não aparecer.
4. Confie no projeto se o Codex perguntar; a configuração `.codex/config.toml` é carregada apenas em projetos confiáveis. Aprove também os hooks de `.codex/hooks.json` se o Codex solicitar.
5. Inicie uma nova conversa e escreva `Use $maestro e explique o que este kit pode fazer.` ou `Use $novo-saas para criar um SaaS...`.
6. Para auditar o pacote, rode `python scripts/validate_codex_project.py` no terminal integrado; a tarefa **Maestro: Validar estrutura Codex** também está em **Terminal > Executar Tarefa**.

Ao abrir esta pasta, o Codex encontra `AGENTS.md`, skills em `.agents/skills/` e os agentes em `.codex/agents/`. **Não é obrigatório rodar `install.sh` ou `install.ps1`** para utilizar o kit nesta pasta.

## 2. Invocar habilidades e delegar

No Codex, digite `$` para encontrar skills (ou utilize `/skills` quando disponível). Os antigos slash-commands do Antigravity foram convertidos para skills:

| Antes (Antigravity) | Agora (Codex) | Finalidade |
| --- | --- | --- |
| `/maestro` | `$maestro` | Coordenar demandas completas |
| `/maestro-orchestrator` | `$maestro-orchestrator` | Alias do Maestro |
| `/novo-saas` | `$novo-saas` | SaaS multi-tenant |
| `/nova-landing-page` | `$nova-landing-page` | Landing page e SEO |
| `/auditoria-seguranca` | `$auditoria-seguranca` | Revisão de riscos |
| `/auditoria-seo` | `$auditoria-seo` | Auditoria Next.js SEO |
| `/deploy-vps` | `$deploy-vps` | Preparar deploy em VPS |
| `/apresentacao-pitch` | `$apresentacao-pitch` | Pitch executivo |
| `/novo-documento-orcamento` | `$novo-documento-orcamento` | Documentação e orçamentos |

Além dos fluxos, as skills técnicas (`$django-mysql-saas`, `$premium-ui-system`, `$nextjs-seo-master`, `$game-canvas-pwa`, `$qa-automated-testing`, `$security-seal-audit`, `$vps-nodocker-deploy`, `$marketing-pitch-showcase`, `$docs-reports-pro`, `$skills-guardian`) continuam disponíveis.

### Exemplo de solicitação

> Use $maestro para criar um sistema de pedidos com Next.js e Django. Planeje etapas, use os especialistas `django_mysql`, `nextjs_frontend` e `qa_testing` quando útil, execute os testes possíveis e peça aprovação antes de qualquer deploy.

Nove subagentes estão em `.codex/agents/*.toml`; o Codex pode ativá-los sob demanda, e **não há garantia de execução paralela em todas as sessões**.

## 3. Instalação global opcional (para outros repositórios)

Se você deseja usar as skills e os agentes também em *outras* pastas do VS Code, rode o instalador da pasta deste kit:

**Linux/macOS:**

```bash
bash install.sh --global
# com permissão para substituir somente os arquivos Maestro já existentes:
# bash install.sh --global --force
```

**Windows PowerShell:**

```powershell
.\install.ps1 -Global
# com permissão para substituir arquivos homônimos:
# .\install.ps1 -Global -Force
```

Os scripts copiam skills para `~/.agents/skills/`, agentes para `~/.codex/agents/` e scripts/templates auxiliares para `~/.codex/maestro/`. Para alertas também em outros projetos, veja `docs/ALERTAS_E_SKILLS.md`, seção **hook global opcional**. Eles **não alteram** o `~/.codex/config.toml` pessoal, **não substituem** o `~/.codex/AGENTS.md` global e pulam arquivos existentes a menos que `--force`/`-Force` seja fornecido. As regras de orquestração do projeto raiz (`AGENTS.md`) ficam nesta pasta; em outros projetos, peça `$maestro` explicitamente.

## 4. Estrutura

```text
AGENTS.md                      # Política lida pelo Codex no projeto
.codex/config.toml             # Subagentes habilitados e limite de paralelismo
.codex/agents/                 # 10 especialistas TOML
.agents/skills/                # 20 skills: 11 tecnicas + 9 fluxos/alias
.agents/workflows/             # Procedimentos legados migrados (referência)
.agents/orchestrator/          # Manual do Maestro
.agents/subagents/             # Especificações originais dos especialistas
.agents/PROJECT_STATE.md       # Modelo de estado factual
.vscode/                       # Extensão recomendada, tarefas e configurações
scripts/validate_codex_project.py
scripts/alert_email.py             # Teste SMTP, alerta e reenvio
scripts/codex_error_hook.py        # Hook de falha Codex
scripts/skills_curator.py          # Sugestoes automaticas para skills
install.sh / install.ps1       # Instalação global opt-in
templates/                     # Exemplos de código/infraestrutura
GUIA_PREMIUM_ECOSSISTEMA.md    # Manual novo de uso Codex
GUIA_PREMIUM_ECOSSISTEMA.pdf   # Versão resumida impressa para Codex
docs/legado-antigravity/       # Material original preservado
```

## 5. Testes e limites

- `python scripts/validate_codex_project.py` verifica estrutura, TOML, frontmatter das skills e caminhos essenciais.
- `bash -n install.sh` verifica sintaxe Bash; a CI também verifica o projeto no GitHub Actions.
- `python templates/security/audit_seal.py` faz checagem estática *parcial*: não certifica OWASP ou segurança para produção.
- Nenhum app SaaS ou instância VPS é criado automaticamente; o usuário deve especificar um sistema/projeto alvo.
- Não fixe chaves de API nem salve senhas no projeto. Revise os templates de produção antes de aplicar em ambiente real.

## Documentação oficial

- [Codex no VS Code](https://learn.chatgpt.com/docs/ide)
- [Configuração de subagentes](https://learn.chatgpt.com/docs/agent-configuration/subagents)
- [Skills do Codex](https://learn.chatgpt.com/docs/build-skills)
- [Configuração de projeto](https://learn.chatgpt.com/docs/config-file/config-basic)

## Créditos

Adaptação preservando os arquivos, templates e a licença MIT do projeto original **antigravity-fullstack-maestro** (ver `LICENSE` e os documentos em `docs/legado-antigravity/`). As marcas Antigravity e Codex têm proprietários distintos. Esta adaptação não é um produto oficial da OpenAI.

## Cloud Deploy

Use `$deploy-mercado3d` ou delegue a `cloud_deploy` via Maestro. Django/React/PostgreSQL, GitHub @savioluz, Render, Vercel, Railway, Neon e Docker opcional. O agente prepara a configuração escolhida e exige autorização antes de publicação, recursos externos, migrações de produção, agendamento ou envio SMTP. Preços/planos são conferidos nas fontes oficiais ao recomendar.

```bash
python3 scripts/cloud_deploy.py inspect mercado3d
python3 scripts/cloud_deploy.py check mercado3d
python3 scripts/cloud_deploy.py check mercado3d --env-check
python3 -m unittest discover -s scripts -p 'test_cloud_deploy.py' -v
```

`--env-check` examina somente as variáveis já fornecidas ao processo, sem ler `.env` nem exibir valores. Inspeção estática não executa testes do aplicativo ou certifica produção. `monitor URL` consulta uma vez o health JSON PostgreSQL; `diagnose LOG` classifica falhas. `--record` nestes dois comandos prepara fila Guardian e outbox local sem enviar e-mail. O envio posterior usa o SMTP existente, após autorização. Não foi instalado monitor residente nem executado deploy.

O aplicativo `savioluz/mercado3d` mantém Git/CI próprios; agentes e scripts do kit permanecem em `savioluz/maestro-codex-agentes`. Os instaladores existentes descobrem os novos arquivos sem alterar configuração global; não foram executados nesta integração. A descoberta do novo agente em sessões futuras depende do Codex autenticado/confiável.
