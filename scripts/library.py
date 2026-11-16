#!/usr/bin/env python3
"""Small, offline-first installer for reviewed Codex components (Python >=3.11)."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import tomllib

ROOT = Path(__file__).resolve().parents[1]


def fail(message):
    raise ValueError(message)


def read_json(path):
    return json.loads(path.read_text())


def write_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + '.tmp')
    with tmp.open('x') as stream:
        json.dump(data, stream, indent=2, ensure_ascii=False)
        stream.write('\n')
    tmp.replace(path)


def safe_path(path):
    """Refuse symlinks at any existing path segment, including the leaf."""
    path = Path(os.path.abspath(path.expanduser()))
    for part in (path, *path.parents):
        if part.is_symlink():
            fail(f'Symlink not allowed: {part}')
    return path


def files(path):
    safe_path(path)
    if path.is_file():
        return [path]
    result = []
    for entry in sorted(path.rglob('*')):
        if entry.is_symlink() or not (entry.is_file() or entry.is_dir()):
            fail(f'Unsupported file: {entry}')
        if entry.is_file():
            result.append(entry)
    return result


def fingerprint(path):
    if not path.exists():
        return None
    result = {(p.relative_to(path).as_posix() if path.is_dir() else '.'): hashlib.sha256(p.read_bytes()).hexdigest()
              for p in files(path)}
    if path.is_dir():
        for entry in path.rglob('*'):
            if entry.is_dir():
                result[entry.relative_to(path).as_posix() + '/'] = 'directory'
    return result


def source_path(component):
    relative = component.get('install_path', component['path'])
    path = safe_path(ROOT / relative)
    if not path.is_relative_to(ROOT) or path == ROOT:
        fail(f'Invalid source path: {relative}')
    return path


def skill_metadata(path):
    text = path.read_text()
    if not text.startswith('---\n') or '\n---' not in text[4:]:
        fail(f'Missing YAML frontmatter: {path}')
    head = text.split('---', 2)[1]
    # Read only name; full YAML semantics and descriptions are checked by Codex.
    match = re.search(r'^name:\s*[\'\"]?([a-zA-Z0-9_-]+)[\'\"]?\s*$', head, re.M)
    if not match or not re.search(r'^description:\s*\S', head, re.M):
        fail(f'Missing name or description: {path}')
    return match.group(1)


def catalog():
    data = read_json(ROOT / 'catalog/components.json')
    if data['schema_version'] != 1:
        fail('Unsupported catalog schema')
    result = {}
    names = set()
    for c in data['components']:
        cid = c['id']
        if not re.fullmatch(r'[a-z0-9][a-z0-9-]*', cid) or cid in result:
            fail(f'Invalid or duplicate id: {cid}')
        if c['type'] not in ('skill', 'agent') or c['review']['status'] != 'approved':
            fail(f'Unapproved component: {cid}')
        if not re.fullmatch(r'[0-9a-f]{40}', c['commit']) or not c['license']:
            fail(f'Missing immutable provenance: {cid}')
        metadata_path = ROOT / 'sources' / (c['source'].replace('/', '--')) / 'metadata.json'
        metadata = read_json(metadata_path)
        if metadata['commit'] != c['commit'] or metadata['repo'] != c['source']:
            fail(f'Source metadata mismatch: {cid}')
        src = source_path(c)
        if not src.exists():
            fail(f'Missing component: {src}')
        if c['type'] == 'skill':
            name = skill_metadata(src / 'SKILL.md')
        else:
            agent = tomllib.loads(src.read_text())
            if set(agent) != {'name', 'description', 'developer_instructions'}:
                fail(f'Unexpected custom agent fields: {cid}')
            if not all(isinstance(v, str) and v.strip() for v in agent.values()):
                fail(f'Empty custom agent field: {cid}')
            name = agent['name']
        if name != c['name'] or (c['type'], name) in names:
            fail(f'Name mismatch or duplicate: {cid}: {name}')
        if not re.fullmatch(r'[a-zA-Z0-9_-]+', name):
            fail(f'Invalid install name: {name}')
        names.add((c['type'], name))
        result[cid] = c
    return result


def validate():
    components = catalog()
    manifest = read_json(ROOT / 'catalog/files.sha256.json')
    expected = {}
    roots = ['skills/external', 'agents/upstream', 'agents/codex', 'sources']
    for folder in roots:
        for p in files(ROOT / folder):
            expected[p.relative_to(ROOT).as_posix()] = hashlib.sha256(p.read_bytes()).hexdigest()
    if expected != manifest:
        changed = sorted(k for k in set(expected) | set(manifest) if expected.get(k) != manifest.get(k))
        fail('Integrity mismatch: ' + ', '.join(changed[:10]))
    profiles = list((ROOT / 'profiles').glob('*.json'))
    if {p.stem for p in profiles} != {'sysadmin', 'devops', 'development', 'wordpress', 'microsoft365', 'security', 'full'}:
        fail('Missing or unexpected installation profile')
    for p in profiles:
        profile = read_json(p)
        ids = profile['components']
        if not ids or len(set(ids)) != len(ids) or set(ids) - components.keys():
            fail(f'Invalid profile: {p.name}')
        if p.stem == 'full' and set(ids) != components.keys():
            fail('Full profile must include all approved components')
    for p in (ROOT / 'integrations/mcp').glob('*.toml'):
        for server in tomllib.loads(p.read_text())['mcp_servers'].values():
            if server.get('enabled') is not False:
                fail(f'MCP template must be disabled: {p}')
    print(f'PASS: {len(components)} components, integrity, profiles and MCP templates')
    return components


def selection(args, components):
    ids = list(args.component or [])
    if args.profile:
        profile = ROOT / 'profiles' / (args.profile + '.json')
        if not profile.is_file():
            fail(f'Unknown profile: {args.profile}')
        ids += read_json(profile)['components']
    if not ids:
        fail('Select --profile NAME or --component ID')
    unknown = set(ids) - components.keys()
    if unknown:
        fail('Unknown components: ' + ', '.join(sorted(unknown)))
    return [components[cid] for cid in dict.fromkeys(ids)]


def locations(args):
    if args.scope == 'project':
        if not args.target:
            fail('Project scope requires --target PATH')
        target = safe_path(args.target)
        if not target.is_dir():
            fail(f'Target project does not exist: {target}')
        skills, codex = target / '.agents/skills', target / '.codex'
    elif args.scope == 'global':
        if args.target:
            fail('--target is only valid with --scope project')
        skills = Path.home() / '.agents/skills'
        codex = Path(os.environ.get('CODEX_HOME', str(Path.home() / '.codex')))
        target = Path.cwd()
    else:
        fail('Specify --scope project or --scope global')
    return target, safe_path(skills), safe_path(codex)


def destination(c, skills, codex):
    return safe_path(skills / c['name'] if c['type'] == 'skill' else codex / 'agents' / (c['name'] + '.toml'))


def load_state(codex):
    path = safe_path(codex / 'internal-ai-library.json')
    if path.exists():
        state = read_json(path)
        if state.get('schema_version') != 1 or not isinstance(state.get('components'), dict):
            fail('Invalid installation state')
        return path, state
    return path, {'schema_version': 1, 'components': {}}


def collision(c, dest, skills, codex):
    directory = skills if c['type'] == 'skill' else codex / 'agents'
    if not directory.exists():
        return
    for candidate in directory.iterdir():
        if candidate == dest:
            continue
        metadata = candidate / 'SKILL.md' if c['type'] == 'skill' else candidate
        if not metadata.is_file():
            continue
        safe_path(metadata)
        try:
            name = skill_metadata(metadata) if c['type'] == 'skill' else tomllib.loads(metadata.read_text()).get('name')
        except (ValueError, OSError):
            fail(f'Cannot inspect existing component safely: {metadata}')
        if name == c['name']:
            fail(f'Existing component with same name: {candidate}')


def mutate(args, components):
    chosen = selection(args, components)
    _, skills, codex = locations(args)
    state_path, state = load_state(codex)
    plan = []
    for c in chosen:
        dest = destination(c, skills, codex)
        collision(c, dest, skills, codex)
        owned = state['components'].get(c['id'])
        current = fingerprint(dest)
        if owned and owned['destination'] != str(dest):
            fail(f'State destination mismatch: {c["id"]}')
        if args.command == 'install':
            if current is not None:
                if owned and current == owned['files'] == fingerprint(source_path(c)):
                    print(f'UNCHANGED {c["id"]}')
                    continue
                fail(f'Already exists; use update for owned unchanged files: {dest}')
            if owned:
                fail(f'Missing owned files; inspect state before reinstalling: {dest}')
        else:
            if not owned:
                fail(f'Component is not managed by this library: {c["id"]}')
            if current != owned['files']:
                fail(f'Local changes or missing files; preserve and reconcile manually: {dest}')
        plan.append((c, dest))
    for c, dest in plan:
        print(f'{"PLAN " if args.dry_run else ""}{args.command.upper()} {c["id"]} -> {dest}')
    if args.dry_run or not plan:
        return
    # Preflight all components above; per-invocation snapshots permit local rollback.
    codex.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='.library-transaction-', dir=codex) as temp:
        backup_root = Path(temp)
        old_state = state_path.read_bytes() if state_path.exists() else None
        touched = []
        try:
            for i, (c, dest) in enumerate(plan):
                backup = backup_root / str(i)
                if dest.exists():
                    if dest.is_dir():
                        shutil.copytree(dest, backup)
                    else:
                        shutil.copy2(dest, backup)
                touched.append((dest, backup))
                if dest.is_dir():
                    shutil.rmtree(dest)
                elif dest.exists():
                    dest.unlink()
                if args.command == 'uninstall':
                    del state['components'][c['id']]
                    continue
                dest.parent.mkdir(parents=True, exist_ok=True)
                src = source_path(c)
                if src.is_dir():
                    shutil.copytree(src, dest)
                else:
                    shutil.copy2(src, dest)
                state['components'][c['id']] = {
                    'destination': str(dest), 'files': fingerprint(dest),
                    'commit': c['commit'], 'source': c['source'], 'type': c['type']}
            write_json(state_path, state)
        except Exception:
            for dest, backup in reversed(touched):
                if dest.is_dir():
                    shutil.rmtree(dest)
                elif dest.exists():
                    dest.unlink()
                if backup.is_dir():
                    shutil.copytree(backup, dest)
                elif backup.exists():
                    shutil.copy2(backup, dest)
            if old_state is not None:
                state_path.write_bytes(old_state)
            elif state_path.exists():
                state_path.unlink()
            raise


def verify(args, components):
    chosen = selection(args, components)
    target, skills, codex = locations(args)
    _, state = load_state(codex)
    for c in chosen:
        dest = destination(c, skills, codex)
        owned = state['components'].get(c['id'])
        if not owned or owned['destination'] != str(dest) or fingerprint(dest) != owned['files']:
            fail(f'Unmanaged, missing or locally changed: {c["id"]}')
        if fingerprint(dest) != fingerprint(source_path(c)):
            fail(f'Installed version differs from reviewed catalog; run update: {c["id"]}')
    print(f'PASS: {len(chosen)} installed components match reviewed catalog')
    if args.codex:
        from codex_probe import probe
        skills_expected = [str(destination(c, skills, codex) / 'SKILL.md') for c in chosen if c['type'] == 'skill']
        probe(target, skills_expected, args.codex_bin)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=['list', 'validate', 'install', 'update', 'uninstall', 'verify', 'check-updates'])
    parser.add_argument('--profile', choices=['sysadmin', 'devops', 'development', 'wordpress', 'microsoft365', 'security', 'full'])
    parser.add_argument('--component', action='append')
    parser.add_argument('--scope', choices=['project', 'global'])
    parser.add_argument('--target', type=Path)
    parser.add_argument('--dry-run', action='store_true')
    parser.add_argument('--codex', action='store_true', help='Ask local Codex app-server to enumerate skills (no model call)')
    parser.add_argument('--codex-bin', help='Codex executable path or name; overrides CODEX_BIN and PATH lookup')
    args = parser.parse_args()
    if args.codex_bin and (args.command != 'verify' or not args.codex):
        parser.error('--codex-bin requires verify --codex')
    try:
        components = validate() if args.command != 'list' else catalog()
        if args.command == 'list':
            chosen = selection(args, components) if args.profile or args.component else components.values()
            for c in chosen:
                print(f'{c["id"]:38} {c["type"]:6} {c["name"]:32} {c["commit"][:12]}')
        elif args.command == 'validate':
            pass
        elif args.command in ('install', 'update', 'uninstall'):
            mutate(args, components)
        elif args.command == 'verify':
            verify(args, components)
        elif args.command == 'check-updates':
            chosen = selection(args, components) if args.profile or args.component else components.values()
            repos = {}
            for c in chosen:
                repos.setdefault(c['source'], set()).add(c['commit'])
            for repo, commits in repos.items():
                if not re.fullmatch(r'[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+', repo):
                    fail(f'Invalid GitHub source: {repo}')
                out = subprocess.check_output(['git', 'ls-remote', '--exit-code', f'https://github.com/{repo}.git', 'HEAD'], text=True, timeout=40)
                latest = out.split()[0]
                print(f'{repo}: {"CURRENT" if commits == {latest} else "REVIEW REQUIRED"} HEAD={latest} pinned={",".join(sorted(commits))}')
    except (ValueError, KeyError, OSError, subprocess.SubprocessError) as error:
        print(f'ERROR: {error}', file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
