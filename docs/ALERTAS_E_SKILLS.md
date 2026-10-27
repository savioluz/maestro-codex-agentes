# Alertas de erro por e-mail + Skills Guardian

**Proprietario:** [@savioluz](https://github.com/savioluz)  
**Destino de alertas:** `savioluz.dev@gmail.com`  
**Canal:** SMTP do Gmail (sem WhatsApp, webhooks de mensagens ou API de terceiros).

## 1. Configurar seu Gmail (obrigatorio para alertas reais)

1. Ative a verificacao em duas etapas da conta Google; se sua conta oferecer a opcao, crie uma **senha de app** de 16 caracteres. Uma conta corporativa pode proibir o recurso.
2. Na raiz do projeto rode `python scripts/setup_email.py` e cole a senha de app no prompt oculto. Ele cria o arquivo local `.env`, ignorado pelo Git.
3. Rode `python scripts/alert_email.py --test` e **verifique o recebimento no Gmail** (inclusive spam). Se o teste falhar, o alerta sera salvo em `.maestro/state/outbox/`.
4. Reenvie os pendentes com `python scripts/alert_email.py --flush` quando houver conectividade/credenciais.
5. Em GitHub, salve a mesma senha de app como **Actions repository secret** chamado `MAESTRO_SMTP_PASSWORD`; nao a salve em variaveis publicas, Issues ou commits.

**Privacidade:** o sistema envia tipo, origem, hora e trecho minimizado do erro, sem prompt inteiro, argumentos completos ou credenciais deliberadamente. Revise logs locais antes de compartilha-los; filtros de segredos nao garantem anonimato absoluto. Os incidentes locais em `.maestro/` podem conter caminhos e fragmentos de logs; nunca versione essa pasta.

## 2. O que dispara os e-mails

- **Codex VS Code / CLI:** `.codex/hooks.json` registra `PostToolUse` e `scripts/codex_error_hook.py` tenta identificar falhas observaveis por status/codigo de saida. No primeiro uso, **confie e aprove os hooks do projeto** no Codex; se aparecer `/hooks`, revise os comandos antes de autorizar.
- **Tarefas VS Code:** `scripts/run_guarded.py -- <comando>` envia alerta se o processo terminar com codigo diferente de zero.
- **GitHub Actions:** o workflow `.github/workflows/email-alerta-ci.yml` roda quando o workflow principal de validacao falha e tenta enviar e-mail, usando o segredo do GitHub.
- **Manualmente:** `python scripts/alert_email.py --title "Minha falha" --message "Descricao curta" --source manual`.

**Limites reais:** nenhum mecanismo consegue garantir aviso de *todo* problema do VS Code, toda mensagem do modelo, erro silencioso de uma aplicacao nao integrada ou falha sem conectividade. O Codex pode nao emitir um `PostToolUse` para certos erros internos/hosted tools. Para apps criados com o kit, integre explicitamente a central de alertas nos testes, pipelines e tratadores de excecoes da propria app. O watcher so funciona com scripts/hook ativos e confiaveis.

Notificacoes iguais sao reduzidas por 30 minutos; a primeira tentativa sem SMTP salva uma mensagem para reenvio posterior. **O pacote nao envia e-mails ate receber sua senha de app/SMTP**. O alerta de falha do GitHub precisa que o repositorio esteja publicado, Actions habilitado e o secret configurado.

## 3. Skills Guardian - aprendizado seguro

- O catalogo `.agents/knowledge/ERROR_CATALOG.json` contem receitas preventivas para 12 tipos de erro (Node, Python, Git, SMTP, Playwright, TS, SQL, TLS e outros).
- A cada falha observada pelos hooks, `scripts/skills_curator.py` associa possiveis solucoes e registra **automaticamente** um incidente em `.maestro/knowledge/incident_suggestions.jsonl`, preparando `.maestro/knowledge/SKILLS_REVIEW_QUEUE.md`.
- Use a skill `$skills-guardian` ou o agente TOML `skills_guardian` para avaliar evidencias, reproduzir o problema e evoluir skills com testes. Hipoteses **nao sobrescrevem habilidades automaticamente**: alteracoes permanentes exigem verificacao e revisao para nao propagar correcao falsa.
- `python scripts/skills_curator.py --report` recompila a fila; `python scripts/skills_curator.py --ingest --title "Exemplo" --detail "EADDRINUSE: 3000"` simula o aprendizado local sem disparar SMTP.

## 4. Integracao Git @savioluz

Na pasta extraida, inicialize Git e ajuste somente a identidade **local**:

```bash
git init
python scripts/git_savioluz.py
git add .
git commit -m "Maestro Codex: alertas email e Skills Guardian"
```

Para criar *um novo repositorio privado* pela CLI GitHub, instale `gh`, faca `gh auth login` para sua conta e execute **apenas se desejar publicar**:

```bash
gh repo create savioluz/maestro-codex-vscode --private --source . --remote origin --push
```

`@savioluz` e seu usuario de GitHub; no caminho remoto use `savioluz` sem `@`. O nome `maestro-codex-vscode` acima e **sugestao de novo repositorio**, nao supomos que ja exista.

## 5. Riscos e manutencao

- Nunca envie senha de app por chat, no Git ou para agente. `.env` ignorado; em GitHub use Secrets.
- SMTP requer acesso de rede; configuracao incorreta ou falha de Gmail geram fila local, nao entrega garantida.
- Se baixar e extrair versao nova, preserve `.env` e a pasta `.maestro/` manualmente; ambos ficam fora do controle de versao.
- E-mail pode conter dados de erro, embora minimizados. Nunca alerte com stack trace completo de producao, tokens, payload de clientes ou dados de saude.

## 6. Opcional: receber alertas do Codex em outros projetos VS Code

O hook dentro de `.codex/hooks.json` monitora **somente este projeto**. Para observar falhas de ferramentas Codex em outras pastas abertas no VS Code, instale scripts e hook **global**, com opt-in (sem sobrescrever hooks existentes):

**Linux/macOS:**

```bash
bash install.sh --global
python scripts/setup_email.py --global
python scripts/install_global_hook.py                # mostra uma prévia, não modifica
python scripts/install_global_hook.py --apply        # altera ~/.codex/hooks.json, com backup
```

**Windows PowerShell:**

```powershell
.\install.ps1 -Global
python scripts/setup_email.py --global
python scripts/install_global_hook.py --apply
```

O instalador de hook **preserva os hooks existentes**, cria cópia de segurança e requer você revisar/confiar no novo hook quando o Codex solicitar (`/hooks`). O script global lê a senha de app de `~/.codex/maestro/.env` (ou `%USERPROFILE%\.codex\maestro\.env`); não reutiliza automaticamente os segredos locais deste projeto. O conjunto global não monitora aplicativos independentes, nem altera projetos alheios. Para atualizá-lo após futuras mudanças no pacote, reinstale com `--force` / `-Force` apenas se tiver revisado as alterações.
