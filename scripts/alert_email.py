#!/usr/bin/env python3
"""Teste SMTP, alerta manual/CI e reenvio de pendentes."""
import argparse
from maestro_alerts import deliver, retry_pending


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--test', action='store_true', help='Enviar email de teste REAL')
    p.add_argument('--flush', action='store_true', help='Reenviar mensagens pendentes')
    p.add_argument('--title', default='Falha reportada')
    p.add_argument('--message', default='Verifique logs no ambiente de origem.')
    p.add_argument('--source', default='manual')
    p.add_argument('--id', default='')
    args = p.parse_args()
    if args.flush:
        done, failed = retry_pending()
        print(f'Reenviados: {done} | pendentes: {failed}')
        return 0 if not failed else 2
    if args.test:
        result = deliver('Teste de alerta SMTP', 'Mensagem de teste do Maestro. Nenhum erro ocorreu.',
                         'setup', fingerprint='test-setup', force=True)
    else:
        result = deliver(args.title, args.message, args.source, fingerprint=args.id or None)
    print(result)
    return 0 if result.startswith(('ENVIADO:', 'DUPLICADO:')) else 2


if __name__ == '__main__':
    raise SystemExit(main())
