# Comandos Git para @savioluz

Perfil: https://github.com/savioluz  
E-mail de autor local: savioluz.dev@gmail.com

## Inicializar o kit (uma unica vez)

```bash
git init
python scripts/git_savioluz.py
git add .
git status
git commit -m "feat: Maestro Codex com monitoramento e Skills Guardian"
```

## Criar repo privado no GitHub (requer GitHub CLI autenticada)

```bash
gh auth login
gh repo create savioluz/maestro-codex-vscode --private --source . --remote origin --push
```

## Atualizar um repo ja publicado

```bash
git status
git add .
git commit -m "chore: evoluir skills e monitoramento Maestro"
git push -u origin HEAD
```

Nao use `git remote add origin` cegamente quando ja houver `origin`. Confira `git remote -v` antes. Nunca publique `.env` ou `.maestro/` - ambos estao no `.gitignore`.

**Avisos no GitHub:** configure em Settings > Secrets and variables > Actions > New repository secret, com nome `MAESTRO_SMTP_PASSWORD`. O GitHub Actions notifica falha no workflow de validacao, nao todos os erros de qualquer repositorio.
