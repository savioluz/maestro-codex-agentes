#!/usr/bin/env python3
"""Opt-in: instala hook global PostToolUse preservando hooks de terceiros."""
from __future__ import annotations
import argparse
import json
import os
import shlex
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path


def global_dir() -> Path:
    return Path(os.environ.get('CODEX_HOME', Path.home()/'.codex')).expanduser()


def installed_hook_script() -> Path:
    return global_dir()/'maestro'/'scripts'/'codex_error_hook.py'


def apply(file: Path, script: Path, preview: bool = True) -> str:
    if not script.exists():
        raise FileNotFoundError('Instale primeiro o kit globalmente: bash install.sh --global ou .\\install.ps1 -Global')
    if file.exists():
        data = json.loads(file.read_text(encoding='utf-8'))
        if not isinstance(data, dict):
            raise ValueError('hooks.json deve ser um objeto JSON; atualizacao abortada')
    else:
        data = {}
    hooks = data.setdefault('hooks', {})
    if not isinstance(hooks, dict):
        raise ValueError('Formato hooks invalido; atualizacao abortada')
    post = hooks.setdefault('PostToolUse', [])
    if not isinstance(post, list):
        raise ValueError('PostToolUse invalido; atualizacao abortada')
    for group in post:
        for handler in group.get('hooks', []):
            if 'codex_error_hook.py' in handler.get('command', ''):
                return 'EXISTE: hook Codex Maestro ja configurado (nenhuma alteracao).'
    command = shlex.join([sys.executable, str(script)])
    windows = subprocess.list2cmdline([sys.executable, str(script)])
    post.append({'hooks': [{'type': 'command', 'command': command,
                             'commandWindows': windows, 'async': True, 'timeout': 25,
                             'statusMessage': 'Maestro: triagem global de falhas'}]})
    if preview:
        return f'PREVISAO: novo hook PostToolUse sera adicionado a {file}. Rode --apply para ativar.'
    file.parent.mkdir(parents=True, exist_ok=True)
    if file.exists():
        backup = file.with_name('hooks.backup-'+datetime.now().strftime('%Y%m%d-%H%M%S')+'.json')
        shutil.copy2(file, backup)
    tmp = file.with_suffix('.tmp')
    tmp.write_text(json.dumps(data, indent=2, ensure_ascii=False)+'\n', encoding='utf-8')
    os.chmod(tmp, 0o600)
    tmp.replace(file)
    return f'CONFIGURADO: {file} (revise/aprove o hook no Codex com /hooks)'


def main():
    p = argparse.ArgumentParser(description='Habilitar e-mail para falhas observadas em QUALQUER projeto do Codex')
    p.add_argument('--apply', action='store_true', help='Modificar hooks globais apos previa revisao')
    args = p.parse_args()
    try:
        print(apply(global_dir()/'hooks.json', installed_hook_script(), preview=not args.apply))
        return 0
    except (OSError, ValueError, TypeError) as e:
        print(f'Falha segura: {type(e).__name__}: {e}', file=sys.stderr)
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
