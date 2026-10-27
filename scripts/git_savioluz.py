#!/usr/bin/env python3
"""Ajusta somente identidade Git do repositorio atual, sem criar repo remoto automaticamente."""
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]


def call(*args):
    return subprocess.run(['git', *args], cwd=ROOT, check=True)


def main():
    if not (ROOT / '.git').exists():
        print('Repositorio ainda nao inicializado. Use `git init` na raiz antes de configurar.')
        return 2
    try:
        call('config', '--local', 'user.name', 'savioluz')
        call('config', '--local', 'user.email', 'savioluz.dev@gmail.com')
        print('Git local: @savioluz / savioluz.dev@gmail.com')
        print('Nenhuma chave, remote, conta ou repositorio GitHub foi alterado.')
    except (OSError, subprocess.CalledProcessError):
        print('Falha na configuracao Git local; confira a instalacao do Git.', file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
