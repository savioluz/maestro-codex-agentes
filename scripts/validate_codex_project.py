#!/usr/bin/env python3
"""Valida arquivos estruturais Codex; não requer login, API, extensões ou dependências."""
from __future__ import annotations
import json
import re
import sys
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AGENTS = {"django_mysql", "nextjs_frontend", "apps_games", "qa_testing", "guardian_security", "vps_nodocker", "marketing_pitch", "docs_reports", "skills_guardian", "cloud_deploy"}
TECH_SKILLS = {"django-mysql-saas", "docs-reports-pro", "game-canvas-pwa", "marketing-pitch-showcase", "nextjs-seo-master", "premium-ui-system", "qa-automated-testing", "security-seal-audit", "vps-nodocker-deploy", "skills-guardian", "deploy-mercado3d"}
WORKFLOWS = {"maestro", "maestro-orchestrator", "apresentacao-pitch", "auditoria-seguranca", "auditoria-seo", "deploy-vps", "nova-landing-page", "novo-documento-orcamento", "novo-saas"}
EXPECTED_FILES = {"AGENTS.md", "README.md", "GUIA_PREMIUM_ECOSSISTEMA.md", ".codex/config.toml", ".vscode/extensions.json", ".vscode/tasks.json", "install.sh", "install.ps1", ".agents/orchestrator/MAESTRO.md", ".agents/PROJECT_STATE.md", ".codex/hooks.json", "scripts/maestro_alerts.py", "scripts/codex_error_hook.py", "scripts/skills_curator.py", "scripts/alert_email.py", "scripts/setup_email.py", "scripts/run_guarded.py", "scripts/git_savioluz.py", "scripts/install_global_hook.py", "scripts/cloud_deploy.py", "scripts/test_cloud_deploy.py", ".agents/knowledge/ERROR_CATALOG.json", ".env.example", "docs/ALERTAS_E_SKILLS.md", ".github/workflows/email-alerta-ci.yml"}

def validate():
    errors=[]
    for filename in sorted(EXPECTED_FILES):
        if not (ROOT/filename).is_file(): errors.append(f"Arquivo essencial ausente: {filename}")
    try:
        c=tomllib.loads((ROOT/".codex/config.toml").read_text(encoding="utf-8"))
        if c.get("agents",{}).get("enabled") is not True: errors.append("Subagentes não habilitados em .codex/config.toml")
        if c.get("agents",{}).get("max_concurrent_threads_per_session",0) < 1: errors.append("Limite de threads inválido")
    except (OSError,ValueError) as ex: errors.append(f"TOML de configuração inválido: {ex}")

    present_agents={p.stem for p in (ROOT/".codex/agents").glob("*.toml")}
    for name in sorted(AGENTS-present_agents): errors.append(f"Agente ausente: {name}")
    for name in sorted(present_agents):
        p=ROOT/".codex/agents"/f"{name}.toml"
        try:
            obj=tomllib.loads(p.read_text(encoding="utf-8"))
            for field in ("name", "description", "developer_instructions"):
                if not isinstance(obj.get(field),str) or not obj[field].strip(): errors.append(f"Agente {name}: {field} ausente ou vazio")
            if obj.get("name")!=name: errors.append(f"Agente {name}: nome não corresponde ao arquivo")
        except (OSError,ValueError) as ex: errors.append(f"Agente {name}: TOML inválido: {ex}")

    allskills=TECH_SKILLS|WORKFLOWS
    present_skills={p.name for p in (ROOT/".agents/skills").iterdir() if p.is_dir()}
    for name in sorted(allskills-present_skills): errors.append(f"Skill ausente: {name}")
    for name in sorted(present_skills):
        p=ROOT/".agents/skills"/name/"SKILL.md"
        if not p.is_file(): errors.append(f"SKILL.md ausente: {name}"); continue
        doc=p.read_text(encoding="utf-8-sig")
        # YAML metadata key-value pairs; declarations are intentionally one line each.
        front=re.match(r"\A---\s*\n(.*?)\n---\s*\n",doc,re.S)
        if front is None: errors.append(f"Frontmatter ausente: {name}"); continue
        vals=dict(re.findall(r"^(name|description):\s*(.+?)\s*$",front.group(1),re.M))
        if vals.get("name")!=name or not vals.get("description"," ").strip(): errors.append(f"Metadados inconsistentes: {name}")
        if "file:///" in doc: errors.append(f"Link local absoluto inválido: {name}")

    for name in sorted(json.loads((ROOT/".vscode/extensions.json").read_text()).get("recommendations",[])):
        if name=="openai.chatgpt": break
    else: errors.append("Extensão Codex não recomendada no VS Code")
    json.loads((ROOT/".vscode/tasks.json").read_text())


    # Hooks, bases de solucoes e configuracao de notificacoes devem ser parseaveis.
    try:
        hooks=json.loads((ROOT/".codex/hooks.json").read_text(encoding="utf-8"))
        post=hooks.get("hooks",{}).get("PostToolUse",[])
        if not post or not any("codex_error_hook.py" in h.get("command","") for group in post for h in group.get("hooks",[])):
            errors.append("Hook PostToolUse de alertas nao configurado")
    except (OSError,ValueError) as ex: errors.append(f"JSON de hooks invalido: {ex}")
    try:
        data=json.loads((ROOT/".agents/knowledge/ERROR_CATALOG.json").read_text(encoding="utf-8"))
        if len(data.get("solutions",[]))<10: errors.append("Catalogo Skills Guardian deve ter no minimo 10 solucoes iniciais")
    except (OSError,ValueError) as ex: errors.append(f"Catalogo Skills Guardian invalido: {ex}")
    env=(ROOT/".env.example").read_text(encoding="utf-8")
    if "MAESTRO_ALERT_TO=savioluz.dev@gmail.com" not in env:
        errors.append("Email de destino nao corresponde ao configurado")
    if "@savioluz" not in (ROOT/".github/CODEOWNERS").read_text(encoding="utf-8"):
        errors.append("GitHub @savioluz nao identificado em CODEOWNERS")

    for f in sorted((ROOT/".agents/workflows").glob("*.md")):
        if "file:///" in f.read_text(encoding="utf-8-sig"): errors.append(f"Link legado absoluto: {f}")
    print(f"Agentes: {len(present_agents)} | Skills: {len(present_skills)} | Workflows: {len(list((ROOT/'.agents/workflows').glob('*.md')))}")
    if errors:
        for err in errors: print(f"[FALHA] {err}")
        return 1
    print("[OK] Estrutura Codex, arquivos TOML, skills e VS Code validados.")
    print("[INFO] Isto NÃO verifica login Codex, delegação ativa ou aplicação de negócio.")
    return 0
if __name__=="__main__": sys.exit(validate())
