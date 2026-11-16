"""Codex executable selection and missing-client regression checks."""
from contextlib import redirect_stdout
import importlib.util
import io
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('codex_probe', ROOT / 'scripts/codex_probe.py')
probe = importlib.util.module_from_spec(spec)
spec.loader.exec_module(probe)


class ExecutableTests(unittest.TestCase):
    def setUp(self):
        (ROOT / '.cache').mkdir(exist_ok=True)
        self.temp = tempfile.TemporaryDirectory(dir=ROOT / '.cache', prefix='codex-path-test-')
        self.addCleanup(self.temp.cleanup)
        self.folder = Path(self.temp.name)
        self.bin = self.folder / 'bin with spaces'
        self.bin.mkdir()
        self.executable = self.bin / 'codex'
        self.executable.write_text('#!/bin/sh\nexit 0\n')
        self.executable.chmod(0o755)
        self.env = patch.dict(os.environ, {'PATH': '', 'CODEX_BIN': ''})
        self.env.start()
        self.addCleanup(self.env.stop)

    def test_missing_binary_explains_completed_and_unrun_checks(self):
        with self.assertRaises(ValueError) as caught:
            probe.resolve_codex()
        message = str(caught.exception)
        self.assertIn('Structural verification passed', message)
        self.assertIn('NOT RUN', message)
        self.assertIn('--codex-bin', message)

    def test_explicit_path_works_without_path_lookup(self):
        self.assertEqual(probe.resolve_codex(str(self.executable)), str(self.executable))

    def test_environment_override_works(self):
        os.environ['CODEX_BIN'] = str(self.executable)
        self.assertEqual(probe.resolve_codex(), str(self.executable))

    def test_explicit_path_overrides_bad_environment(self):
        os.environ['CODEX_BIN'] = str(self.folder / 'missing')
        self.assertEqual(probe.resolve_codex(str(self.executable)), str(self.executable))

    def test_invalid_explicit_path_does_not_fall_back(self):
        os.environ['PATH'] = str(self.bin)
        with self.assertRaises(ValueError):
            probe.resolve_codex(str(self.folder / 'missing'))

    def test_default_path_discovery_is_preserved(self):
        os.environ['PATH'] = str(self.bin)
        self.assertEqual(probe.resolve_codex(), str(self.executable))

    def test_relative_path_is_absolute_before_project_cwd_changes(self):
        relative = os.path.relpath(self.executable, Path.cwd())
        self.assertEqual(probe.resolve_codex(relative), str(self.executable))

    def test_cli_requires_live_verification_with_explicit_binary(self):
        result = subprocess.run([sys.executable, str(ROOT / 'scripts/library.py'), 'validate',
                                 '--codex-bin', str(self.executable)], capture_output=True, text=True)
        self.assertEqual(result.returncode, 2)
        self.assertIn('--codex-bin requires verify --codex', result.stderr)

    def test_missing_codex_preserves_successful_installed_verification(self):
        spec = importlib.util.spec_from_file_location('library_probe_test', ROOT / 'scripts/library.py')
        library = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(library)
        from types import SimpleNamespace
        args = SimpleNamespace(command='install', component=['sysadmin-monitor'], profile=None,
                               scope='project', target=self.folder, dry_run=False)
        with redirect_stdout(io.StringIO()):
            library.mutate(args, library.catalog())
        state = self.folder / '.codex/internal-ai-library.json'
        original = state.read_bytes()
        command = [sys.executable, str(ROOT / 'scripts/library.py'), 'verify', '--scope', 'project',
                   '--target', str(self.folder), '--component', 'sysadmin-monitor']
        plain = subprocess.run(command, capture_output=True, text=True)
        live = subprocess.run(command + ['--codex'], capture_output=True, text=True)
        self.assertEqual(plain.returncode, 0, plain.stderr)
        self.assertEqual(live.returncode, 1)
        self.assertIn('PASS: 1 installed components', live.stdout)
        self.assertIn('NOT RUN', live.stderr)
        self.assertEqual(state.read_bytes(), original)
