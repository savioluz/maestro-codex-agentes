#!/usr/bin/env bash
# Instalacao opcional global das skills e dos subagentes para Codex. Nao modifica config.toml.
set -euo pipefail

usage() {
  cat <<'EOF'
Maestro para Codex / VS Code

Usar nesta pasta do VS Code: nenhuma instalacao e necessaria.
Instalar em outros projetos (diretorios do usuario):
  bash install.sh --global
  bash install.sh --global --force    # substitui somente itens Maestro homonimos
EOF
}

GLOBAL=0
FORCE=0
for arg in "$@"; do
  case "$arg" in
    --global) GLOBAL=1 ;;
    --force) FORCE=1 ;;
    -h|--help) usage; exit 0 ;;
    *) echo "Argumento nao reconhecido: $arg" >&2; usage; exit 2 ;;
  esac
done
if [[ "$GLOBAL" -ne 1 ]]; then usage; exit 0; fi

SOURCE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_TARGET="${HOME}/.agents/skills"
AGENT_TARGET="${CODEX_HOME:-${HOME}/.codex}/agents"
TOOLS_TARGET="${CODEX_HOME:-${HOME}/.codex}/maestro"
mkdir -p "$SKILL_TARGET" "$AGENT_TARGET" "$TOOLS_TARGET"

copy_safe() {
  local src="$1" dest="$2"
  if [[ -e "$dest" || -L "$dest" ]]; then
    if [[ "$FORCE" -ne 1 ]]; then
      echo "[PULADO] Ja existe: $dest (use --force para substituir)"
      return
    fi
    # Remove apenas o item exato do Maestro, quando explicitamente autorizado.
    rm -rf -- "$dest"
  fi
  cp -R -- "$src" "$dest"
  echo "[OK] $dest"
}

for src in "$SOURCE_DIR"/.agents/skills/*; do
  [[ -d "$src" && -f "$src/SKILL.md" ]] || continue
  copy_safe "$src" "$SKILL_TARGET/$(basename "$src")"
done
for src in "$SOURCE_DIR"/.codex/agents/*.toml; do
  [[ -f "$src" ]] || continue
  copy_safe "$src" "$AGENT_TARGET/$(basename "$src")"
done

for rel in templates scripts .agents/orchestrator .agents/workflows .agents/subagents; do
  src="$SOURCE_DIR/$rel"
  [[ -d "$src" ]] || continue
  copy_safe "$src" "$TOOLS_TARGET/$(basename "$rel")"
done
copy_safe "$SOURCE_DIR/.agents/skills" "$TOOLS_TARGET/skills"
mkdir -p "$TOOLS_TARGET/.agents"
copy_safe "$SOURCE_DIR/.agents/knowledge" "$TOOLS_TARGET/.agents/knowledge"

echo
echo 'Instalacao global concluida (sem modificar AGENTS.md global nem config.toml).'
echo 'Reabra a conversa do Codex e use $maestro em seu projeto.'
