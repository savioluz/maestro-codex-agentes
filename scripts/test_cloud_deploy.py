"""Regressões Cloud Deploy: diagnóstico sem execução/publicação e fila sem SMTP."""
import contextlib
import io
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch, MagicMock

import cloud_deploy as cloud
import skills_curator


class CloudDeployTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def project(self):
        for folder in ('.git', 'backend/config', 'frontend', '.github/workflows'):
            (self.root / folder).mkdir(parents=True)
        for name, content in {
            'backend/manage.py': 'raise RuntimeError("must not execute")',
            'backend/config/settings.py': 'DATABASES = {"default": "postgresql"}',
            'backend/requirements.lock.txt': 'Django==5.2',
            'frontend/package.json': json.dumps({'dependencies': {'react': '19'}}),
            'frontend/package-lock.json': '{}',
            'frontend/Dockerfile': 'CMD ["npm", "run", "dev"]',
            'render.yaml': 'services: []',
            '.github/workflows/ci.yml': 'name: test',
            '.env': 'DO_NOT_READ=this-is-private',
        }.items():
            (self.root / name).write_text(content)

    def test_inspection_detects_stack_without_running_project_or_reading_env(self):
        self.project()
        original = Path.read_text
        def checked(path, *args, **kwargs):
            self.assertNotEqual(path.name, '.env')
            return original(path, *args, **kwargs)
        with patch.object(Path, 'read_text', checked):
            report = cloud.check_project(self.root)
        self.assertTrue(report['ok'])
        self.assertTrue(report['architecture']['postgresql'])
        self.assertFalse(report['production_approved'])
        self.assertFalse(report['pricing_verified'])
        self.assertIn('development_container_not_production', [x['code'] for x in report['findings']])

    def test_missing_lock_and_independent_repo_are_blockers(self):
        (self.root / 'package.json').write_text('{"dependencies":{"react":"19"}}')
        report = cloud.check_project(self.root)
        self.assertFalse(report['ok'])
        self.assertIn('separate_git_repository_required', [x['code'] for x in report['findings']])
        self.assertIn('frontend_lockfile_missing', [x['code'] for x in report['findings']])

    def test_symlink_outside_project_is_not_read(self):
        outside = self.root / 'outside'; outside.mkdir()
        target = outside / 'settings.py'; target.write_text('postgresql')
        project = self.root / 'project'; (project / 'backend').mkdir(parents=True)
        (project / 'backend/manage.py').write_text('')
        (project / 'backend/config').symlink_to(outside, target_is_directory=True)
        self.assertFalse(cloud.inspect_project(project)['architecture']['postgresql'])

    def test_environment_validates_without_exposing_values(self):
        values = {'DJANGO_SECRET_KEY': 'X'*55, 'DJANGO_DEBUG': 'false',
                  'DATABASE_URL': 'postgresql://owner:never-print@db.example/app?sslmode=require',
                  'DJANGO_ALLOWED_HOSTS': 'api.example', 'CORS_ALLOWED_ORIGINS': 'https://shop.example',
                  'CSRF_TRUSTED_ORIGINS': 'https://shop.example'}
        with patch.dict(os.environ, values, clear=True):
            self.assertEqual(cloud.check_environment(), [])
            os.environ['DJANGO_DEBUG'] = 'true'
            os.environ['DATABASE_URL'] = 'postgresql://owner:never-print@db.example/app'
            findings = cloud.check_environment()
        self.assertIn('database_tls_required', [x['code'] for x in findings])
        self.assertNotIn('never-print', json.dumps(findings))

    def test_monitor_rejects_secrets_http_remote_and_redirect(self):
        for url in ('http://example.com/api/health/', 'https://user:pass@example.com/',
                    'https://example.com/?token=abc', 'file:///etc/passwd'):
            with self.assertRaises(ValueError):
                cloud.validate_url(url)
        cloud.validate_url('http://127.0.0.1:8001/api/health/')
        self.assertIsNone(cloud.NoRedirect().redirect_request(None, None, 302, '', {}, 'https://evil.example'))

    def test_monitor_checks_postgres_health_not_just_http_200(self):
        response = MagicMock(status=200)
        response.__enter__.return_value = response
        opener = MagicMock()
        opener.open.return_value = response
        with patch.object(cloud.request, 'build_opener', return_value=opener):
            for body, expected in [(b'{"status":"ok","database":"postgresql"}', True),
                                   (b'{"status":"ok","database":"sqlite"}', False), (b'<html>login</html>', False)]:
                response.read.return_value = body
                self.assertEqual(cloud._monitor_once('https://example.com/api/health/')['ok'], expected)
        self.assertEqual(opener.open.call_args.kwargs['timeout'], 10)

    def test_repeated_tls_options_are_rejected(self):
        with patch.dict(os.environ, {'DATABASE_URL': 'postgresql://u:p@db/app?sslmode=require&sslmode=disable'}, clear=True):
            codes = [x['code'] for x in cloud.check_environment()]
        self.assertIn('database_tls_required', codes)

    def test_monitor_has_total_deadline_and_cleans_up_only_own_worker(self):
        context = MagicMock()
        context.Pipe.return_value = (MagicMock(), MagicMock())
        process = context.Process.return_value
        process.pid = 123
        process.is_alive.return_value = True
        with patch.object(cloud.multiprocessing, 'get_context', return_value=context):
            result = cloud.monitor('https://example.com/api/health/')
        self.assertEqual(result['code'], 'health_deadline_exceeded')
        process.join.assert_any_call(timeout=12)
        process.terminate.assert_called_once()
        process.kill.assert_called_once()

    def test_invalid_manifest_returns_structured_error(self):
        (self.root / 'package.json').write_text('[]')
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            self.assertEqual(cloud.main(['inspect', str(self.root)]), 2)
        self.assertEqual(json.loads(output.getvalue())['code'], 'invalid_input')

    def test_record_prepares_outbox_and_guardian_never_sends(self):
        with patch.object(cloud, 'STATE', self.root / 'state'), \
             patch.object(skills_curator, 'INBOX', self.root / 'incidents.jsonl'), \
             patch.object(skills_curator, 'REVIEW', self.root / 'review.md'), \
             patch('maestro_alerts._smtp_send') as smtp:
            report = cloud.record_failure({'ok': False, 'code': 'ECONNREFUSED'})
            cloud.record_failure({'ok': False, 'code': 'ECONNREFUSED'})
        smtp.assert_not_called()
        self.assertEqual(report['learning_status'], 'SUGERIDO_NAO_TESTADO')
        self.assertEqual(report['notification'], 'queued_locally_not_sent')
        self.assertEqual(len(list((self.root / 'state/outbox').glob('*.json'))), 1)
        self.assertTrue((self.root / 'review.md').exists())

    def test_specific_cloud_recipes_take_precedence(self):
        self.assertEqual(cloud.match_error('OperationalError: password authentication failed')['id'], 'cloud-postgres')
        for code in ('health_deadline_exceeded', 'health_worker_error'):
            self.assertEqual(cloud.match_error(code)['id'], 'cloud-health')
        self.assertEqual(cloud.match_error('Build failed')['id'], 'cloud-build')

    def test_diagnosis_does_not_echo_sensitive_log(self):
        log = self.root / 'build.log'
        log.write_text('ModuleNotFoundError password=never-print')
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            rc = cloud.main(['diagnose', str(log)])
        self.assertEqual(rc, 1)
        self.assertIn('python-modulo-ausente', output.getvalue())
        self.assertNotIn('never-print', output.getvalue())

    def test_invalid_input_is_structured_without_sensitive_argument(self):
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            self.assertEqual(cloud.main(['monitor', 'https://user:secret@example.com']), 2)
        self.assertNotIn('secret', output.getvalue())
        self.assertEqual(json.loads(output.getvalue())['code'], 'invalid_input')


if __name__ == '__main__':
    unittest.main()
