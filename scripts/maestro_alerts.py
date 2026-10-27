#!/usr/bin/env python3
"""Central de incidentes + e-mail SMTP (stdlib, sem segredos versionados)."""
from __future__ import annotations
import hashlib
import json
import os
import re
import smtplib
import ssl
import tempfile
import time
from datetime import datetime, timezone
from email.message import EmailMessage
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STATE = ROOT / '.maestro' / 'state'
ALLOWED_SETTINGS = {
    'MAESTRO_ALERT_TO', 'MAESTRO_SMTP_USER', 'MAESTRO_SMTP_PASSWORD',
    'MAESTRO_SMTP_HOST', 'MAESTRO_SMTP_PORT', 'MAESTRO_SMTP_SSL',
    'MAESTRO_EMAIL_ENABLED',
}


def config() -> dict[str, str]:
    values: dict[str, str] = {}
    envfile = ROOT / '.env'
    if envfile.is_file():
        for raw in envfile.read_text(encoding='utf-8').splitlines():
            line = raw.strip()
            if not line or line.startswith('#') or '=' not in line:
                continue
            key, value = line.split('=', 1)
            if key.strip() in ALLOWED_SETTINGS:
                values[key.strip()] = value.strip().strip('"').strip("'")
    for key in ALLOWED_SETTINGS:
        if key in os.environ:
            values[key] = os.environ[key]
    values.setdefault('MAESTRO_ALERT_TO', 'savioluz.dev@gmail.com')
    values.setdefault('MAESTRO_SMTP_HOST', 'smtp.gmail.com')
    values.setdefault('MAESTRO_SMTP_PORT', '465')
    values.setdefault('MAESTRO_SMTP_SSL', 'true')
    values.setdefault('MAESTRO_EMAIL_ENABLED', '1')
    return values


def sanitize(value: object, size: int = 1200) -> str:
    s = str(value)
    s = re.sub(r'(?i)\b(bearer)\s+\S+', r'\1 [OCULTO]', s)
    s = re.sub(r'(?i)\b(password|passwd|secret|token|api[_-]?key|authorization|smtp[_-]?password)\b\s*[:=]\s*[^\s,;]+', r'\1=[OCULTO]', s)
    s = re.sub(r'\b(?:gh[pousr]_[A-Za-z0-9_]{12,}|github_pat_[A-Za-z0-9_]+)\b', '[TOKEN OCULTO]', s)
    s = re.sub(r'(?i)(postgres(?:ql)?|mysql|mongodb(?:\+srv)?)://[^\s/@]+:[^\s/@]+@', r'\1://[CREDENCIAIS OCULTAS]@', s)
    s = re.sub(r'[\x00-\x08\x0b-\x1f\x7f]', '', s)
    return s[:size]


def _atomic_json(path: Path, data: object):
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=path.parent, prefix='.tmp-')
    try:
        with os.fdopen(fd, 'w', encoding='utf-8') as stream:
            json.dump(data, stream, indent=2, ensure_ascii=False)
        os.chmod(tmp, 0o600)
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)


def _smtp_send(title: str, body: str, settings: dict[str, str]):
    if settings.get('MAESTRO_EMAIL_ENABLED') != '1':
        raise RuntimeError('Alertas desativados por MAESTRO_EMAIL_ENABLED')
    user, password = settings.get('MAESTRO_SMTP_USER'), settings.get('MAESTRO_SMTP_PASSWORD')
    recipient = settings.get('MAESTRO_ALERT_TO')
    if not user or not password or not recipient:
        raise RuntimeError('SMTP nao configurado; execute python scripts/setup_email.py')
    msg = EmailMessage()
    msg['From'] = user
    msg['To'] = recipient
    msg['Subject'] = sanitize(title, 120).replace('\n', ' ')
    msg.set_content(sanitize(body, 2500))
    host = settings['MAESTRO_SMTP_HOST']
    port = int(settings['MAESTRO_SMTP_PORT'])
    tls_ctx = ssl.create_default_context()
    if settings['MAESTRO_SMTP_SSL'].lower() in ('true', '1', 'yes'):
        with smtplib.SMTP_SSL(host, port, timeout=10, context=tls_ctx) as smtp:
            smtp.login(user, password)
            smtp.send_message(msg)
    else:
        with smtplib.SMTP(host, port, timeout=10) as smtp:
            smtp.starttls(context=tls_ctx)
            smtp.login(user, password)
            smtp.send_message(msg)


def deliver(title: str, detail: str, source: str, fingerprint: str | None = None,
            dry_run: bool = False, force: bool = False) -> str:
    """Nao mascara falha de envio. Fila local quando SMTP indisponivel."""
    title, detail, source = sanitize(title, 120), sanitize(detail, 1800), sanitize(source, 100)
    key = hashlib.sha256((fingerprint or f'{source}|{title}|{detail[:150]}').encode('utf-8')).hexdigest()[:24]
    mail = (f'Origem: {source}\nMomento UTC: {datetime.now(timezone.utc).isoformat(timespec="seconds")}\n'
            f'Evento: {title}\n\nDetalhes resumidos:\n{detail}\n\nID: {key}\n'
            '\nAviso automatico do Maestro. Credenciais e comandos completos nao sao anexados.')
    if dry_run:
        return f'SIMULACAO: {title} -> {config()["MAESTRO_ALERT_TO"]}'
    now = time.time()
    history = STATE / 'sent.json'
    try:
        sent = json.loads(history.read_text(encoding='utf-8')) if history.exists() else {}
    except (ValueError, OSError):
        sent = {}
    if not force and now - float(sent.get(key, 0)) < 1800:
        return f'DUPLICADO: {key} (limite de 30 min)'
    try:
        _smtp_send(f'[Maestro ERRO] {title}', mail, config())
    except (OSError, smtplib.SMTPException, ValueError, RuntimeError) as exc:
        pending = STATE / 'outbox' / f'{key}.json'
        _atomic_json(pending, {'title': title, 'detail': detail, 'source': source, 'key': key, 'created_utc': datetime.now(timezone.utc).isoformat()})
        return f'PENDENTE ({type(exc).__name__}): incidente salvo em .maestro/state/outbox/{key}.json'
    sent[key] = now
    _atomic_json(history, {k: v for k, v in sent.items() if now-float(v) < 172800})
    pending = STATE / 'outbox' / f'{key}.json'
    pending.unlink(missing_ok=True)
    return f'ENVIADO: {config()["MAESTRO_ALERT_TO"]}'


def retry_pending() -> tuple[int, int]:
    done = failed = 0
    for path in sorted((STATE / 'outbox').glob('*.json')):
        try:
            obj = json.loads(path.read_text(encoding='utf-8'))
            result = deliver(obj['title'], obj['detail'], obj['source'], obj['key'], force=True)
            done += result.startswith('ENVIADO:')
            failed += not result.startswith('ENVIADO:')
        except (OSError, ValueError, KeyError, TypeError):
            failed += 1
    return done, failed
