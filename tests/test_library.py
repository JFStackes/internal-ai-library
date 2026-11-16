"""Installer boundary and lifecycle regressions. All writes stay under repo .cache."""
from contextlib import redirect_stdout
import importlib.util
import io
import json
from pathlib import Path
import subprocess
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('library', ROOT / 'scripts/library.py')
lib = importlib.util.module_from_spec(spec)
spec.loader.exec_module(lib)


class LibraryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.components = lib.catalog()
        (ROOT / '.cache').mkdir(exist_ok=True)

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(dir=ROOT / '.cache', prefix='unit-')
        self.addCleanup(self.temp.cleanup)
        self.target = Path(self.temp.name)
        self.args = SimpleNamespace(command='install', scope='project', target=self.target,
                                    profile=None, component=['sysadmin-monitor'], dry_run=False, codex=False)
        self.dest = self.target / '.agents/skills/sysadmin-monitor'
        self.state = self.target / '.codex/internal-ai-library.json'

    def run_action(self, command='install'):
        self.args.command = command
        with redirect_stdout(io.StringIO()):
            lib.mutate(self.args, self.components)

    def test_all_profiles_install_verify_update_and_uninstall(self):
        for profile in ['sysadmin', 'devops', 'development', 'wordpress', 'microsoft365', 'security', 'full']:
            with self.subTest(profile=profile):
                self.args.profile, self.args.component = profile, None
                self.run_action()
                self.run_action()  # second install is idempotent
                self.run_action('update')
                with redirect_stdout(io.StringIO()):
                    lib.verify(self.args, self.components)
                self.run_action('uninstall')
                self.assertEqual(json.loads(self.state.read_text())['components'], {})

    def test_dry_run_never_creates_installation(self):
        self.args.dry_run = True
        self.run_action()
        self.assertFalse(self.state.exists())
        self.assertFalse(self.dest.exists())

    def test_unmanaged_destination_not_overwritten(self):
        self.dest.mkdir(parents=True)
        sentinel = self.dest / 'custom.txt'
        sentinel.write_text('keep me')
        with self.assertRaisesRegex(ValueError, 'Already exists'):
            self.run_action()
        self.assertEqual(sentinel.read_text(), 'keep me')
        self.assertFalse(self.state.exists())

    def test_local_changes_block_update_and_uninstall(self):
        self.run_action()
        extra = self.dest / 'local-work.txt'
        extra.write_text('operator change')
        for action in ['install', 'update', 'uninstall']:
            with self.assertRaises(ValueError):
                self.run_action(action)
        self.assertEqual(extra.read_text(), 'operator change')

    def test_symlinked_destination_is_rejected(self):
        outside = self.target / 'keep'
        outside.mkdir()
        self.dest.parent.mkdir(parents=True)
        self.dest.symlink_to(outside, target_is_directory=True)
        with self.assertRaisesRegex(ValueError, 'Symlink'):
            self.run_action()
        self.assertEqual(list(outside.iterdir()), [])

    def test_symlinked_parent_is_rejected(self):
        outside = self.target / 'keep'
        outside.mkdir()
        (self.target / '.agents').symlink_to(outside, target_is_directory=True)
        with self.assertRaisesRegex(ValueError, 'Symlink'):
            self.run_action()
        self.assertEqual(list(outside.iterdir()), [])

    def test_internal_symlink_blocks_uninstall(self):
        self.run_action()
        (self.dest / 'escape').symlink_to(self.target)
        with self.assertRaisesRegex(ValueError, 'Unsupported file'):
            self.run_action('uninstall')
        self.assertTrue(self.state.exists())

    def test_same_skill_name_in_different_folder_is_rejected(self):
        other = self.dest.parent / 'other-folder'
        other.mkdir(parents=True)
        (other / 'SKILL.md').write_text('---\nname: sysadmin-monitor\ndescription: Existing\n---\n')
        with self.assertRaisesRegex(ValueError, 'same name'):
            self.run_action()
        self.assertFalse(self.dest.exists())

    def test_same_agent_name_in_different_file_is_rejected(self):
        self.args.component = ['agent-m365-admin']
        other = self.target / '.codex/agents/other.toml'
        other.parent.mkdir(parents=True)
        other.write_text('name="m365-admin"\ndescription="Existing"\ndeveloper_instructions="Keep"\n')
        with self.assertRaisesRegex(ValueError, 'same name'):
            self.run_action()
        self.assertEqual(len(list(other.parent.iterdir())), 1)

    def test_whole_selection_preflight_prevents_partial_install(self):
        self.args.component = ['sysadmin-monitor', 'sysadmin-diagnose']
        blocked = self.dest.parent / 'sysadmin-diagnose'
        blocked.mkdir(parents=True)
        with self.assertRaises(ValueError):
            self.run_action()
        self.assertFalse(self.dest.exists())

    def test_uninstall_requires_ownership(self):
        with self.assertRaisesRegex(ValueError, 'not managed'):
            self.run_action('uninstall')

    def test_tampered_state_destination_cannot_delete_other_path(self):
        self.run_action()
        data = json.loads(self.state.read_text())
        data['components']['sysadmin-monitor']['destination'] = str(self.target)
        self.state.write_text(json.dumps(data))
        with self.assertRaisesRegex(ValueError, 'destination mismatch'):
            self.run_action('uninstall')
        self.assertTrue(self.dest.exists())

    def test_copy_failure_rolls_back_existing_files_and_state(self):
        self.args.component = ['sysadmin-monitor', 'agent-m365-admin']
        self.run_action()
        previous = self.state.read_bytes()
        before = lib.fingerprint(self.dest)
        original = lib.shutil.copy2

        def interrupted(src, dst, *a, **kw):
            if Path(src).parent == ROOT / 'agents/codex':
                raise OSError('simulated disk failure')
            return original(src, dst, *a, **kw)

        with patch.object(lib.shutil, 'copy2', side_effect=interrupted):
            with self.assertRaisesRegex(OSError, 'disk failure'):
                self.run_action('update')
        self.assertEqual(previous, self.state.read_bytes())
        self.assertEqual(before, lib.fingerprint(self.dest))
        self.assertTrue((self.target / '.codex/agents/m365-admin.toml').is_file())

    def test_reviewed_new_version_replaces_owned_unchanged_version(self):
        self.run_action()
        newer = self.target / 'reviewed-copy'
        lib.shutil.copytree(lib.source_path(self.components['sysadmin-monitor']), newer)
        (newer / 'revision.txt').write_text('reviewed upstream update')
        revised = dict(self.components['sysadmin-monitor'], path=str(newer.relative_to(ROOT)), commit='b' * 40)
        updated_catalog = dict(self.components, **{'sysadmin-monitor': revised})
        self.args.command = 'update'
        with redirect_stdout(io.StringIO()):
            lib.mutate(self.args, updated_catalog)
            lib.verify(self.args, updated_catalog)
        self.assertEqual((self.dest / 'revision.txt').read_text(), 'reviewed upstream update')
        self.assertEqual(json.loads(self.state.read_text())['components']['sysadmin-monitor']['commit'], 'b' * 40)

    def test_new_empty_directory_is_preserved_as_local_change(self):
        self.run_action()
        (self.dest / 'operator-folder').mkdir()
        with self.assertRaisesRegex(ValueError, 'Local changes'):
            self.run_action('uninstall')

    def test_validator_detects_tampered_vendored_skill(self):
        fixture = self.target / 'library-fixture'
        fixture.mkdir()
        c = self.components['sysadmin-monitor']
        for folder in ['skills/external', 'agents/upstream', 'agents/codex', 'sources', 'catalog', 'profiles']:
            (fixture / folder).mkdir(parents=True)
        lib.shutil.copytree(lib.source_path(c), fixture / c['path'])
        metadata = Path('sources') / c['source'].replace('/', '--') / 'metadata.json'
        (fixture / metadata).parent.mkdir(parents=True)
        lib.shutil.copy2(ROOT / metadata, fixture / metadata)
        (fixture / 'catalog/components.json').write_text(json.dumps({'schema_version': 1, 'components': [c]}))
        for profile in ['sysadmin', 'devops', 'development', 'wordpress', 'microsoft365', 'security', 'full']:
            (fixture / 'profiles' / (profile + '.json')).write_text(json.dumps({'components': [c['id']]}))
        manifest = {p.relative_to(fixture).as_posix(): lib.hashlib.sha256(p.read_bytes()).hexdigest()
                    for folder in ['skills/external', 'sources'] for p in lib.files(fixture / folder)}
        (fixture / 'catalog/files.sha256.json').write_text(json.dumps(manifest))
        with patch.object(lib, 'ROOT', fixture), redirect_stdout(io.StringIO()):
            lib.validate()
            (fixture / c['path'] / 'SKILL.md').write_text('---\nname: sysadmin-monitor\ndescription: altered\n---\nChanged workflow')
            with self.assertRaisesRegex(ValueError, 'Integrity mismatch'):
                lib.validate()

    def test_unknown_component_rejected(self):
        self.args.component = ['nonexistent']
        with self.assertRaisesRegex(ValueError, 'Unknown'):
            self.run_action()

    def test_scope_is_required(self):
        self.args.scope = None
        with self.assertRaisesRegex(ValueError, 'Specify --scope'):
            self.run_action()

    def test_global_scope_paths_without_writing_real_home(self):
        # Path resolution only. No global install is performed.
        with patch.object(Path, 'home', return_value=self.target), patch.dict(lib.os.environ, {'CODEX_HOME': str(self.target / 'custom-codex')}):
            self.args.scope, self.args.target = 'global', None
            _, skills, codex = lib.locations(self.args)
            self.assertEqual(skills, self.target / '.agents/skills')
            self.assertEqual(codex, self.target / 'custom-codex')
            self.assertFalse(codex.exists())

    def test_public_cli_outside_repository_cwd(self):
        result = subprocess.run([str(ROOT / 'scripts/library.sh'), 'list', '--profile', 'microsoft365'],
                                cwd=self.target, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('clim365', result.stdout)


if __name__ == '__main__':
    unittest.main()
