#!/usr/bin/env python3
"""Hook Codex PostToolUse: detectar falhas observaveis sem interpretar falha como sucesso."""
from __future__ import annotations
import json
import re
import sys
from maestro_alerts import deliver, sanitize
from skills_curator import ingest, rebuild_review


def response_excerpt(data: object) -> str | None:
    if isinstance(data, dict):
        for name in ('exit_code', 'exitCode', 'returncode', 'return_code'):
            if name in data:
                try:
                    if int(data[name]) != 0:
                        return sanitize(data.get('stderr') or data.get('output') or data.get('stdout') or f'Saida com codigo {data[name]}')
                    return None
                except (TypeError, ValueError):
                    pass
        if data.get('isError') is True or data.get('is_error') is True or data.get('success') is False:
            return sanitize(data.get('error') or data.get('message') or data.get('output') or str(data))
        if str(data.get('status', '')).lower() in ('failed', 'error', 'failure'):
            return sanitize(data.get('error') or data.get('message') or str(data))
        if isinstance(data.get('content'), list):
            if any(isinstance(v, dict) and v.get('type') == 'error' for v in data['content']):
                return sanitize(data['content'])
        if isinstance(data.get('metadata'), dict):
            nested = response_excerpt(data['metadata'])
            if nested:
                return sanitize(data.get('output') or data.get('stderr') or nested)
        if isinstance(data.get('result'), dict):
            return response_excerpt(data['result'])
        return None
    if isinstance(data, str):
        # Algumas implementacoes do Codex serializam a resposta como texto.
        m = re.search(r'(?:Process exited with code|exit code|Exit code:)\s*(\d+)', data, re.I)
        if m and int(m.group(1)) != 0:
            return sanitize(data)
    return None


def handle(event: dict):
    if event.get('hook_event_name') != 'PostToolUse':
        return 'IGNORADO: evento nao monitorado'
    problem = response_excerpt(event.get('tool_response'))
    if problem is None:
        return 'OK: ferramenta sem falha detectada'
    source = 'codex:' + sanitize(event.get('tool_name') or 'ferramenta', 80)
    title = f'Falha em {source}'
    reference = sanitize(event.get('tool_use_id') or '', 80)
    incident = ingest(source, title, problem, reference)
    rebuild_review()
    status = deliver(title, problem + '\nHipotese: ' + incident['candidate_solution'], source,
                     fingerprint=f"{source}|{incident['catalog_id']}|{problem[:200]}")
    return status + f" | catalogo: {incident['catalog_id']}"


if __name__ == '__main__':
    try:
        content = sys.stdin.read(32768)
        payload = json.loads(content)
        if isinstance(payload, dict):
            print(handle(payload), file=sys.stderr)
    except Exception as exc:
        # Hook de notificacao nunca deve bloquear trabalho nem vazar dados.
        print('Maestro hook: falha interna ' + type(exc).__name__, file=sys.stderr)
    sys.exit(0)
