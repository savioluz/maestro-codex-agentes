#!/usr/bin/env python3
"""Cloud Deploy: diagnóstico local e healthcheck único; nunca publica ou envia e-mail."""
from __future__ import annotations

import argparse
import hashlib
import ipaddress
import json
import multiprocessing
import os
from datetime import datetime, timezone
from pathlib import Path
from urllib import error, parse, request

from maestro_alerts import STATE, _atomic_json, sanitize
from skills_curator import ingest, match_error, rebuild_review

IGNORED = {'.git', '.venv', 'venv', 'node_modules', 'dist', '__pycache__', '.maestro'}


def read_local(root: Path, relative: str) -> str:
    path = root / relative
    if not path.resolve().is_relative_to(root) or path.is_symlink():
        return ''
    if path.is_file() and path.stat().st_size < 2_000_000:
        return path.read_text(encoding='utf-8', errors='replace')
    return ''


def inspect_project(project: Path) -> dict:
    root = project.resolve(strict=True)
    if not root.is_dir():
        raise ValueError('Diretório de projeto obrigatório.')
    package_file = 'frontend/package.json' if (root / 'frontend/package.json').exists() else 'package.json'
    package_text = read_local(root, package_file)
    package = json.loads(package_text) if package_text else {}
    if not isinstance(package, dict) or any(not isinstance(package.get(k, {}), dict) for k in ('dependencies', 'devDependencies')):
        raise ValueError('Manifest de dependências inválido.')
    deps = {**package.get('dependencies', {}), **package.get('devDependencies', {})}
    backend = 'backend' if (root / 'backend/manage.py').is_file() else '.'
    django = (root / backend / 'manage.py').is_file()
    settings = []
    # Pesquisa limitada à árvore de backend, sem importar Python ou executar código.
    for current, dirs, files in os.walk(root / backend, followlinks=False):
        dirs[:] = [d for d in dirs if d not in IGNORED and not (Path(current) / d).is_symlink()]
        if len(Path(current).relative_to(root).parts) > 5:
            dirs[:] = []
            continue
        if 'settings.py' in files:
            settings.append(read_local(root, str((Path(current) / 'settings.py').relative_to(root))))
    postgres = any('postgres' in s.lower() for s in settings)
    frontend_dir = 'frontend' if package_file.startswith('frontend/') else '.'
    configs = [name for name in ('render.yaml', 'vercel.json', 'railway.json', 'railway.toml',
        'docker-compose.yml', 'compose.yaml', 'backend/Dockerfile', 'frontend/Dockerfile') if read_local(root, name)]
    workflows = root / '.github/workflows'
    ci = sorted(p.name for p in workflows.glob('*') if p.is_file() and p.suffix in {'.yml', '.yaml'} and p.resolve().is_relative_to(root))
    independent = (root / '.git').is_dir() or (root / '.git').is_file()
    return {
        'architecture': {'django': django, 'react': 'react' in deps, 'postgresql': postgres,
                         'backend_dir': backend, 'frontend_dir': frontend_dir},
        'independent_repository': independent,
        'expected_repository': 'savioluz/mercado3d' if root.name.lower() == 'mercado3d' else 'savioluz/<projeto>',
        'agent_repository': 'savioluz/maestro-codex-agentes',
        'configs': configs, 'ci_workflows': ci,
        'hosting_candidates': [
            {'frontend': 'Render Static ou Vercel', 'backend': 'Render ou Railway', 'database': 'Neon PostgreSQL',
             'reason': 'Separar assets estáticos de Django; reutilizar Render existente quando adequado.' if 'render.yaml' in configs else 'Comparar implantação unificada com frontend estático separado.',
             'tradeoffs': ['cold start e quotas', 'região e latência do banco', 'conexões/pooling', 'domínios/cookies de sessão', 'custo total e backup']}
        ] if django and 'react' in deps and postgres else [],
        'pricing_verified': False,
        'next_decision': 'Consultar planos oficiais atuais, carga, região e orçamento antes de escolher hospedagem.',
        'external_changes': False,
    }


def check_environment() -> list[dict]:
    findings = []
    def fail(code, name):
        findings.append({'level': 'error', 'code': code, 'variable': name})
    required = ('DATABASE_URL', 'DJANGO_SECRET_KEY', 'DJANGO_DEBUG', 'DJANGO_ALLOWED_HOSTS',
                'CORS_ALLOWED_ORIGINS', 'CSRF_TRUSTED_ORIGINS')
    for name in required:
        if not os.environ.get(name, '').strip():
            fail('missing_environment', name)
    if os.environ.get('DJANGO_DEBUG', '').lower() != 'false':
        fail('debug_must_be_false', 'DJANGO_DEBUG')
    secret = os.environ.get('DJANGO_SECRET_KEY', '')
    if len(secret) < 50 or any(word in secret.lower() for word in ('example', 'changeme', 'placeholder', 'ci-only')):
        fail('unsafe_secret', 'DJANGO_SECRET_KEY')
    hosts = os.environ.get('DJANGO_ALLOWED_HOSTS', '')
    if '*' in hosts or '://' in hosts:
        fail('invalid_allowed_hosts', 'DJANGO_ALLOWED_HOSTS')
    for name in ('CORS_ALLOWED_ORIGINS', 'CSRF_TRUSTED_ORIGINS'):
        for origin in os.environ.get(name, '').split(','):
            parsed = parse.urlsplit(origin.strip())
            if parsed.scheme != 'https' or not parsed.hostname or parsed.username or parsed.path not in ('', '/') or parsed.query or parsed.fragment:
                fail('https_origin_required', name)
                break
    db = parse.urlsplit(os.environ.get('DATABASE_URL', ''))
    if db.scheme not in ('postgres', 'postgresql') or not db.hostname or not db.path.strip('/'):
        fail('postgresql_url_required', 'DATABASE_URL')
    ssl_modes = parse.parse_qs(db.query, keep_blank_values=True).get('sslmode', [])
    if len(ssl_modes) != 1 or ssl_modes[0] not in ('require', 'verify-ca', 'verify-full'):
        fail('database_tls_required', 'DATABASE_URL')
    if os.environ.get('DEMO_ALLOW_ROLE_SELECTION', 'false').lower() != 'false':
        fail('public_role_selection', 'DEMO_ALLOW_ROLE_SELECTION')
    return findings


def check_project(project: Path, env_check: bool = False) -> dict:
    report = inspect_project(project)
    root = project.resolve()
    findings = []
    def note(code, level='warning'):
        findings.append({'level': level, 'code': code})
    a = report['architecture']
    if not report['independent_repository']:
        note('separate_git_repository_required', 'error')
    if not (a['django'] and a['react'] and a['postgresql']):
        note('review_detected_architecture')
    if a['react'] and not read_local(root, str(Path(a['frontend_dir']) / 'package-lock.json')):
        note('frontend_lockfile_missing', 'error')
    if a['django'] and not any(read_local(root, str(Path(a['backend_dir']) / f)) for f in ('requirements.lock.txt', 'uv.lock', 'poetry.lock')):
        note('backend_lockfile_missing', 'error')
    if not report['ci_workflows']:
        note('ci_missing')
    for config in ('docker-compose.yml', 'compose.yaml', 'frontend/Dockerfile', 'backend/Dockerfile'):
        text = read_local(root, config)
        if any(marker in text for marker in ('runserver', 'npm run dev', '"dev"')):
            findings.append({'level': 'warning', 'code': 'development_container_not_production', 'file': config})
    if env_check:
        findings.extend(check_environment())
    report.update(findings=findings, ok=not any(f['level'] == 'error' for f in findings),
                  verification='static_only', production_approved=False,
                  pending_checks=['testes backend em banco descartável', 'build e E2E frontend',
                                  'Django check --deploy em ambiente alvo', 'dependency scanning',
                                  'cookies/CSRF/origem via navegador', 'backup/restauração em cópia', 'aprovação humana antes de publicação'])
    return report


class NoRedirect(request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def validate_url(url: str):
    parsed = parse.urlsplit(url)
    host = parsed.hostname
    local = host == 'localhost'
    try:
        local = local or ipaddress.ip_address(host or '').is_loopback
    except ValueError:
        pass
    if not host or parsed.username or parsed.password or parsed.query or parsed.fragment:
        raise ValueError('Healthcheck exige URL sem credenciais, query ou fragmento.')
    if parsed.scheme != 'https' and not (parsed.scheme == 'http' and local):
        raise ValueError('Healthcheck remoto exige HTTPS; HTTP permitido apenas em loopback.')
    if parsed.port == 0:
        raise ValueError('Porta inválida.')


def _monitor_once(url: str) -> dict:
    validate_url(url)
    # Não segue redirects, não executa scripts e não registra corpo nem URL que possa conter dados.
    try:
        opener = request.build_opener(NoRedirect())
        with opener.open(request.Request(url, headers={'Accept': 'application/json', 'User-Agent': 'Maestro-Cloud-Deploy/1'}), timeout=10) as response:
            body = response.read(65537)
            if len(body) > 65536:
                return {'ok': False, 'code': 'health_response_too_large'}
            payload = json.loads(body)
            ok = response.status == 200 and isinstance(payload, dict) and payload.get('status') == 'ok' and payload.get('database') == 'postgresql'
            return {'ok': ok, 'code': 'healthy' if ok else 'invalid_health_payload', 'http_status': response.status}
    except error.HTTPError as exc:
        return {'ok': False, 'code': 'http_error', 'http_status': exc.code}
    except (OSError, ValueError, error.URLError):
        return {'ok': False, 'code': 'health_connection_or_payload_error'}


def _monitor_worker(url, connection):
    try:
        connection.send(_monitor_once(url))
    except Exception:
        connection.send({'ok': False, 'code': 'health_worker_error'})
    finally:
        connection.close()


def monitor(url: str) -> dict:
    validate_url(url)
    # Processo próprio garante prazo total mesmo com headers/corpo enviados lentamente.
    context = multiprocessing.get_context('spawn')
    reader, writer = context.Pipe(duplex=False)
    process = context.Process(target=_monitor_worker, args=(url, writer), daemon=True)
    try:
        process.start()
        writer.close()
        process.join(timeout=12)
        if process.is_alive():
            return {'ok': False, 'code': 'health_deadline_exceeded'}
        if reader.poll():
            try:
                return reader.recv()
            except EOFError:
                pass
        return {'ok': False, 'code': 'health_worker_error'}
    finally:
        if process.pid and process.is_alive():
            process.terminate()
            process.join(timeout=1)
            if process.is_alive():
                process.kill()
                process.join(timeout=1)
        reader.close()
        writer.close()


def record_failure(report: dict):
    detail = sanitize(json.dumps(report, ensure_ascii=False), 1600)
    title = 'Cloud Deploy: verificação falhou'
    incident = ingest('cloud-deploy', title, detail)
    rebuild_review()
    key = hashlib.sha256(('cloud-deploy|' + detail).encode()).hexdigest()[:24]
    _atomic_json(STATE / 'outbox' / f'{key}.json', {
        'title': title, 'detail': detail, 'source': 'cloud-deploy', 'key': key,
        'created_utc': datetime.now(timezone.utc).isoformat(),
    })
    return {'catalog_id': incident['catalog_id'], 'notification': 'queued_locally_not_sent',
            'learning_status': 'SUGERIDO_NAO_TESTADO'}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    for mode in ('inspect', 'check'):
        command = sub.add_parser(mode)
        command.add_argument('project', type=Path)
        if mode == 'check':
            command.add_argument('--env-check', action='store_true', help='Valida somente ambiente do processo, sem ler .env.')
    command = sub.add_parser('monitor', help='Uma consulta GET; agendamento é separado e requer aprovação.')
    command.add_argument('url')
    command.add_argument('--record', action='store_true', help='Prepara fila local Guardian/SMTP em caso de falha; não envia.')
    command = sub.add_parser('diagnose')
    command.add_argument('log', type=Path)
    command.add_argument('--record', action='store_true')
    args = parser.parse_args(argv)
    try:
        if args.command == 'inspect':
            result = inspect_project(args.project)
        elif args.command == 'check':
            result = check_project(args.project, args.env_check)
        elif args.command == 'monitor':
            result = monitor(args.url)
            result['target_id'] = hashlib.sha256(args.url.encode()).hexdigest()[:16]
        else:
            # Não executa o conteúdo do log; não o devolve ao terminal.
            with args.log.open(encoding='utf-8', errors='replace') as stream:
                detail = sanitize(stream.read(65536), 16000)
            result = {'ok': False, 'diagnosis': match_error(detail), 'status': 'SUGERIDO_NAO_TESTADO'}
        if getattr(args, 'record', False) and not result.get('ok', True):
            result['record'] = record_failure(result)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 1 if result.get('ok') is False else 0
    except (OSError, ValueError, TypeError) as exc:
        # Nenhum argumento/caminho/conteúdo sensível é repetido em mensagens de erro.
        print(json.dumps({'ok': False, 'code': 'invalid_input', 'error_type': type(exc).__name__}))
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
