#!/usr/bin/env python3
"""Executa um comando e, em falha, gera incidente e tenta email. Sem shell=True."""
from __future__ import annotations
import argparse
import subprocess
import sys
from collections import deque
from maestro_alerts import deliver, sanitize
from skills_curator import ingest, rebuild_review


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('command', nargs=argparse.REMAINDER)
    args = parser.parse_args()
    cmd = args.command[1:] if args.command[:1] == ['--'] else args.command
    if not cmd:
        parser.error('Informe comando apos --')
    tail = deque(maxlen=12)
    try:
        # Mostra log no terminal e guarda somente um trecho final para diagnostico.
        with subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                              text=True, errors='replace', bufsize=1) as proc:
            if proc.stdout:
                for line in proc.stdout:
                    sys.stdout.write(line)
                    sys.stdout.flush()
                    tail.append(line.rstrip())
            rc = proc.wait()
    except OSError as exc:
        rc = 127
        tail.append(f'Falha ao iniciar executavel: {type(exc).__name__}')
        print('Maestro: impossivel iniciar executavel', file=sys.stderr)
    if rc:
        title = f'Tarefa VS Code falhou (codigo {rc})'
        # NAO enviar argumentos completos (podem conter segredos).
        detail = sanitize(f'Executavel: {cmd[0]}; codigo de saida: {rc}\n'+'\n'.join(tail), 1600)
        incident = ingest('vscode-task', title, detail)
        rebuild_review()
        print(deliver(title, detail, 'vscode-task', fingerprint=title+'|'+cmd[0]+'|'+detail[:250]), file=sys.stderr)
        print(f"Skills Guardian: {incident['candidate_solution']}", file=sys.stderr)
    return rc


if __name__ == '__main__':
    sys.exit(main())
