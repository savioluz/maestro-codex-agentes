#!/usr/bin/env python3
"""Sugestoes automaticas e seguras de correcoes; promocao manual apos testes."""
from __future__ import annotations
import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path

from maestro_alerts import ROOT, sanitize

CATALOG = ROOT / '.agents' / 'knowledge' / 'ERROR_CATALOG.json'
INBOX = ROOT / '.maestro' / 'knowledge' / 'incident_suggestions.jsonl'
REVIEW = ROOT / '.maestro' / 'knowledge' / 'SKILLS_REVIEW_QUEUE.md'


def catalog():
    return json.loads(CATALOG.read_text(encoding='utf-8'))['solutions']


def match_error(detail: str):
    for row in catalog():
        if any(re.search(signal, detail, re.I) for signal in row['signals']):
            return row
    return {
        'id': 'diagnostico-pendente', 'skills': ['skills-guardian'],
        'diagnostic': 'Reproduzir em ambiente isolado, registrar stack trace minimizado e identificar a causa raiz.',
        'candidate_solution': 'Ainda sem reparo validado: pesquisar documentacao e escrever um teste que reproduza a falha.',
        'verify': 'Executar o teste que falhava e a suite de regressao.'
    }


def ingest(source: str, title: str, detail: str, reference: str = '') -> dict:
    entry = match_error(detail)
    data = {
        'date_utc': datetime.now(timezone.utc).isoformat(timespec='seconds'),
        'source': sanitize(source, 90),
        'title': sanitize(title, 160),
        'excerpt': sanitize(detail, 500),
        'reference': sanitize(reference, 100),
        'catalog_id': entry['id'],
        'skills': entry['skills'],
        'diagnostic': entry['diagnostic'],
        'candidate_solution': entry['candidate_solution'],
        'verify': entry['verify'],
        'status': 'SUGERIDO_NAO_TESTADO',
    }
    INBOX.parent.mkdir(parents=True, exist_ok=True)
    with INBOX.open('a', encoding='utf-8') as outfile:
        outfile.write(json.dumps(data, ensure_ascii=False) + '\n')
    return data


def rebuild_review():
    entries = []
    if INBOX.exists():
        for line in INBOX.read_text(encoding='utf-8').splitlines():
            try:
                entries.append(json.loads(line))
            except ValueError:
                continue
    blocks = ['# Fila de aprendizado - Maestro Skills Guardian',
              '', 'Sugestoes sao **hipoteses**, nao correcoes comprovadas. Valide antes de mudar SKILL.md.', '']
    for item in entries[-100:][::-1]:
        blocks += [f"## {item['date_utc']} - {item['title']}",
                   f"- Origem: `{item['source']}`; categoria: `{item['catalog_id']}`; skills: {', '.join(item['skills'])}",
                   f"- Evidencia minimizada: `{item['excerpt']}`",
                   f"- Diagnosticar: {item['diagnostic']}",
                   f"- Correcao sugerida (nao testada): {item['candidate_solution']}",
                   f"- Como verificar: {item['verify']}", '']
    REVIEW.parent.mkdir(parents=True, exist_ok=True)
    REVIEW.write_text('\n'.join(blocks) + '\n', encoding='utf-8')
    return len(entries)


def main():
    p = argparse.ArgumentParser(description='Maestro Skills Guardian - fila de aprendizado')
    p.add_argument('--report', action='store_true', help='Atualizar a fila e exibir contagem')
    p.add_argument('--ingest', action='store_true', help='Adicionar erro manual')
    p.add_argument('--source', default='manual')
    p.add_argument('--title', default='Falha nao classificada')
    p.add_argument('--detail', default='Erro nao especificado')
    args = p.parse_args()
    if args.ingest:
        data = ingest(args.source, args.title, args.detail)
        print(f"[{data['catalog_id']}] sugestao registrada. Status: NAO TESTADO")
    print(f'Incidentes preparados para revisao: {rebuild_review()}')


if __name__ == '__main__':
    main()
