"""Ask the installed Codex parser to discover skills without invoking any model."""
import json
import os
from pathlib import Path
import selectors
import shutil
import subprocess
import tempfile
import time


def resolve_codex(binary=None):
    requested = binary or os.environ.get('CODEX_BIN') or 'codex'
    executable = shutil.which(os.path.expanduser(requested))
    if not executable:
        raise ValueError(
            f'Codex executable not found: {requested!r}. '
            'Structural verification passed; live discovery was NOT RUN. '
            'Use verify without --codex for file checks only, or specify '
            '--codex --codex-bin /absolute/path/to/codex (or set CODEX_BIN).'
        )
    # Popen runs in the installed project; resolve relative paths before changing cwd.
    return str(Path(executable).resolve())


def probe(target, expected, binary=None):
    executable = resolve_codex(binary)
    cache = Path(__file__).resolve().parents[1] / '.cache'
    cache.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='codex-probe-', dir=cache) as temp:
        env = dict(os.environ, CODEX_HOME=temp, XDG_CACHE_HOME=str(Path(temp) / 'cache'),
                   XDG_STATE_HOME=str(Path(temp) / 'state'), TMPDIR=temp)
        with (Path(temp) / 'stderr.log').open('w') as err:
            proc = subprocess.Popen([executable, 'app-server', '--listen', 'stdio://'],
                                    cwd=target, env=env, stdin=subprocess.PIPE,
                                    stdout=subprocess.PIPE, stderr=err)
            selector = selectors.DefaultSelector()
            selector.register(proc.stdout, selectors.EVENT_READ)
            buffer = b''

            def send(message):
                proc.stdin.write(json.dumps(message).encode() + b'\n')
                proc.stdin.flush()

            def response(request_id):
                nonlocal buffer
                deadline = time.monotonic() + 35
                while time.monotonic() < deadline:
                    while b'\n' in buffer:
                        line, buffer = buffer.split(b'\n', 1)
                        result = json.loads(line)
                        if result.get('id') == request_id:
                            if 'error' in result:
                                raise ValueError(f'Codex RPC rejected discovery: {result["error"]}')
                            return result['result']
                    if not selector.select(timeout=max(0, deadline - time.monotonic())):
                        break
                    chunk = os.read(proc.stdout.fileno(), 65536)
                    if not chunk:
                        raise ValueError('Codex app-server exited before discovery; check version compatibility')
                    buffer += chunk
                raise ValueError('Codex discovery timed out')

            try:
                send({'id': 1, 'method': 'initialize', 'params': {'clientInfo': {'name': 'internal-ai-library', 'version': '1.0'}}})
                response(1)
                send({'method': 'initialized', 'params': {}})
                send({'id': 2, 'method': 'skills/list', 'params': {'cwds': [str(target)], 'forceReload': True}})
                result = response(2)
                discovered = {}
                errors = []
                for entry in result.get('data', []):
                    errors.extend(entry.get('errors', []))
                    for skill in entry.get('skills', []):
                        if skill.get('enabled', True):
                            discovered[str(Path(skill['path']).resolve())] = skill['name']
                missing = [p for p in expected if str(Path(p).resolve()) not in discovered]
                if errors or missing:
                    raise ValueError(f'Codex discovery errors={errors}; missing={missing}')
                print(f'PASS: installed Codex discovered {len(expected)} selected Skills via skills/list (no model call)')
                print('Agents: TOML schema checked locally; spawning is not tested by this probe.')
            finally:
                selector.close()
                proc.terminate()
                try:
                    proc.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    proc.kill()
                    proc.wait()
                proc.stdin.close()
                proc.stdout.close()
