# Working in Internal AI Library

This repository curates reusable third-party components for local OpenAI Codex clients. Start with [README.md](README.md), [architecture](docs/architecture.md), [source decisions](docs/research.md) and the dated [verification record](docs/verification.md). Spanish operator documentation is [docs/README.es.md](docs/README.es.md).

## Entry points and ownership

- `scripts/library.sh`: public CLI; `scripts/library.py`: Python standard-library implementation.
- `catalog/`: approved component metadata, provenance and integrity records.
- `profiles/`: installation selections; use actual catalog IDs.
- `skills/external/`: original approved skill directories.
- `agents/upstream/`: original third-party agent files; `agents/codex/`: supported Codex adapters.
- `sources/`: upstream metadata and licenses.
- `integrations/mcp/`: separate MCP recipes, disabled until explicitly configured.
- `tests/`: meaningful installer and validation regression tests.
- `docs/contributing.md`: authoritative source approval and update procedure.

## Invariants

1. Reuse established external components before authoring new skills or agent personas. Preserve originals, license notices and immutable origin commits; document adapters separately.
2. Keep Skills, custom agents, repository instructions and MCP servers distinct. Do not invent Codex settings or claim unsupported tools exist.
3. Never execute vendored scripts as part of fetching, installation or validation. Review script behavior and dependencies before task-specific execution.
4. Never store credentials, populated environment files, tokens, tenant data or production output. MCP configuration uses environment references or supported interactive authentication.
5. Default to read-only operations and minimum permissions. Obtain explicit authorization for destructive operations. Agent prose does not enforce a sandbox.
6. Do not overwrite unmanaged installations or local edits. Updates use approved local versions; remote update discovery does not approve code.
7. During initial setup and maintenance scoped to this repository, use isolated targets beneath `.cache/`. Do not install globally, modify sibling projects, connect production services or push unless the user authorizes that scope.
8. Keep English and Spanish operator READMEs synchronized. Report actual checks and limitations; static validation is not authenticated integration acceptance.

## Required checks

```bash
./scripts/library.sh validate
python3 -m unittest discover -s tests -v
```

For changes to installation or Codex discovery, exercise installation, repeat installation, verification, update and uninstall against a disposable target beneath `.cache/`. Use `verify --codex` when a compatible local client is available. Record the client version and separate unsupported or unavailable checks from failures.

## Delegation

Use specialized subagents when the user or an applicable instruction explicitly requests delegation and the work can be bounded. Give each agent a clear task and file ownership; keep source approval and integration decisions with the primary agent. Skills supply workflows, custom agent TOML files supply roles, and parent-session permissions and available MCP servers constrain both. Do not assume that installing an agent automatically delegates work.
