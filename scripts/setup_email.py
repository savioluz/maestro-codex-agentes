#!/usr/bin/env python3
"""Configura Gmail SMTP localmente sem exibir nem versionar credencial."""
from __future__ import annotations
import argparse
import getpass
import os
import stat
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--global', dest='global_env', action='store_true', help='Credencial para o hook global Codex')
    args = parser.parse_args()
    root = (Path(os.environ.get('CODEX_HOME', Path.home() / '.codex')) / 'maestro') if args.global_env else ROOT
    root.mkdir(parents=True, exist_ok=True)
    file = root / '.env'
    print('Maestro: configuracao local de alertas para savioluz.dev@gmail.com')
    if file.exists():
        print('Arquivo .env ja existe. Para nao sobrescrever credenciais, edite-o manualmente.')
        return 1
    print('Ative a verificacao em duas etapas e use uma SENHA DE APP do Gmail (nao sua senha de login).')
    app_pass = getpass.getpass('Cole aqui a SENHA DE APP (oculta): ').strip()
    if not app_pass:
        print('Configuracao cancelada: nenhuma senha foi gravada.')
        return 1
    content = '\n'.join([
        'MAESTRO_ALERT_TO=savioluz.dev@gmail.com',
        'MAESTRO_SMTP_USER=savioluz.dev@gmail.com',
        'MAESTRO_SMTP_HOST=smtp.gmail.com',
        'MAESTRO_SMTP_PORT=465',
        'MAESTRO_SMTP_SSL=true',
        'MAESTRO_EMAIL_ENABLED=1',
        'MAESTRO_SMTP_PASSWORD='+app_pass.replace(' ', ''), '',
    ])
    fd = os.open(file, os.O_WRONLY | os.O_CREAT | os.O_EXCL, stat.S_IRUSR | stat.S_IWUSR)
    try:
        with os.fdopen(fd, 'w', encoding='utf-8') as stream:
            stream.write(content)
    except Exception:
        file.unlink(missing_ok=True)
        raise
    print('Credencial salva apenas em arquivo .env privado: ' + str(file))
    print('Envie um teste REAL usando o script da mesma pasta dos arquivos de configuracao.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
