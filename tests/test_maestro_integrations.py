"""Testes sem rede e sem email real - nao exigem pytest."""
from __future__ import annotations
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import maestro_alerts
import codex_error_hook
import skills_curator


class TestAlertas(unittest.TestCase):
    def test_sanitizacao(self):
        s = maestro_alerts.sanitize('password=abc123 token: XYZZ bearer SECRET github_pat_ABCDEF12345678909876')
        self.assertNotIn('abc123', s)
        self.assertNotIn('XYZZ', s)
        self.assertNotIn('SECRET', s)
        self.assertNotIn('github_pat_', s)

    def test_resposta_sucesso_ignorada(self):
        self.assertIsNone(codex_error_hook.response_excerpt({'exit_code': 0, 'output': '0 errors'}))
        self.assertIsNone(codex_error_hook.response_excerpt('All good'))

    def test_falha_com_exit_code(self):
        self.assertIn('EADDRINUSE', codex_error_hook.response_excerpt({'exit_code': 1, 'stderr': 'EADDRINUSE: 3000'}))
        self.assertIsNotNone(codex_error_hook.response_excerpt({'metadata': {'exit_code': 7}, 'output': 'failure'}))

    def test_catalogo(self):
        self.assertEqual(skills_curator.match_error('ModuleNotFoundError: No module named x')['id'], 'python-modulo-ausente')
        self.assertEqual(skills_curator.match_error('EADDRINUSE: 3000')['id'], 'porta-em-uso')
        self.assertEqual(skills_curator.match_error('ABC erro novo xyz')['id'], 'diagnostico-pendente')

    def test_fila_sem_smtp(self):
        with tempfile.TemporaryDirectory() as temp:
            with patch.object(maestro_alerts, 'STATE', Path(temp)), \
                    patch.object(maestro_alerts, 'config', return_value={'MAESTRO_ALERT_TO': 'savioluz.dev@gmail.com'}):
                result = maestro_alerts.deliver('falha', 'EADDRINUSE', 'unittest', fingerprint='f1')
                self.assertIn('PENDENTE', result)
                self.assertEqual(len(list((Path(temp)/'outbox').glob('*.json'))), 1)

    def test_smtp_mock_e_dedup(self):
        with tempfile.TemporaryDirectory() as temp:
            with patch.object(maestro_alerts, 'STATE', Path(temp)), \
                    patch.object(maestro_alerts, '_smtp_send') as smtp:
                sent = maestro_alerts.deliver('falha', 'teste', 'unittest', fingerprint='f2')
                dup = maestro_alerts.deliver('falha', 'teste', 'unittest', fingerprint='f2')
                self.assertIn('ENVIADO:', sent)
                self.assertIn('DUPLICADO:', dup)
                smtp.assert_called_once()

    def test_hook_alimenta_fila_sem_enviar_email(self):
        with tempfile.TemporaryDirectory() as temp:
            with patch.object(skills_curator, 'INBOX', Path(temp)/'incident.jsonl'), \
                 patch.object(skills_curator, 'REVIEW', Path(temp)/'review.md'), \
                 patch.object(codex_error_hook, 'deliver', return_value='EMAIL_SIMULADO'):
                result = codex_error_hook.handle({
                    'hook_event_name': 'PostToolUse', 'tool_name': 'Bash',
                    'tool_use_id': 'tool-1', 'tool_response': {'exit_code': 1, 'output': 'npm ERR! ERESOLVE'},
                })
                self.assertIn('EMAIL_SIMULADO', result)
                stored = json.loads((Path(temp)/'incident.jsonl').read_text().splitlines()[0])
                self.assertEqual(stored['catalog_id'], 'npm-deps')
                self.assertEqual(stored['status'], 'SUGERIDO_NAO_TESTADO')
                self.assertTrue((Path(temp)/'review.md').exists())


if __name__ == '__main__':
    unittest.main()
