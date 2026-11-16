# Internal AI Library

[Leer en español](docs/README.es.md)

A private, versioned library of reusable third-party Skills, specialized agents and MCP integration recipes for OpenAI Codex. Upstream components are selected and reviewed before inclusion; original files, licenses and immutable Git commits remain traceable.

The library covers SysAdmin, DevOps, development, WordPress, Microsoft 365, security, and AI automation where suitable components are available. [Research and selection decisions](docs/research.md) record coverage and exclusions. Installing a profile never starts an MCP server or changes infrastructure.

## Requirements

- Bash, Python 3.11 or newer, and Git.
- A current local Codex client for discovery and optional runtime verification.
- Linux, macOS or WSL for the Bash entry point. Native Windows installation is not verified.

Installation and local validation use the checked-in collection and need no network. Checking upstream updates and connecting MCP servers require network access. Individual Skills may require additional tools; inspect their instructions before use.

## Start safely inside this repository

```bash
./scripts/library.sh list
./scripts/library.sh validate
mkdir -p .cache/demo
./scripts/library.sh install --scope project --target .cache/demo --profile sysadmin --dry-run
./scripts/library.sh install --scope project --target .cache/demo --profile sysadmin
./scripts/library.sh verify --scope project --target .cache/demo --profile sysadmin
./scripts/library.sh verify --scope project --target .cache/demo --profile sysadmin --codex
```

Open Codex from the installed target directory. Use `/skills` or `$skill-name` in the CLI or IDE. Ask explicitly to delegate a bounded task to an installed agent. Codex must support the current standalone agent format; permissions, authentication and available tools still come from the parent session.

`verify` checks installed files without requiring a Codex executable. The optional `--codex` check additionally requires `codex` on your terminal's `PATH`. If it is elsewhere, use `verify ... --codex --codex-bin /absolute/path/to/codex`, or set `CODEX_BIN`. Selection order is `--codex-bin`, `CODEX_BIN`, then `codex` on `PATH`. A missing executable leaves file checks successful but makes the requested live check fail with `NOT RUN`; nothing is reinstalled. See [troubleshooting](docs/usage.md#codex-no-está-en-el-path).

## Profiles and individual components

Available profiles: `sysadmin`, `devops`, `development`, `wordpress`, `microsoft365`, `security`, `full`. AI automation components are included in the relevant profiles and `full`. Inspect `profiles/` and `list` before choosing `full`, which can add substantial skill context.

Select individual components with repeated `--component ID` instead of `--profile NAME`; `list` supplies the IDs. Project installation writes only beneath the chosen target. Global installation is supported through explicit `--scope global`; it is not needed for the quick start and was not performed during repository setup.

| Component | Project location | Global location |
| --- | --- | --- |
| Skills | `.agents/skills/<skill-name>/` | `~/.agents/skills/<skill-name>/` |
| Custom agents | `.codex/agents/<agent>.toml` | `$CODEX_HOME/agents/`, default `~/.codex/agents/` |
| Installation manifest | `.codex/internal-ai-library.json` | `$CODEX_HOME/internal-ai-library.json` |

Existing unmanaged installations are protected. Updates and removal require ownership records and unchanged installed content. Resolve local modifications deliberately; there is no force-overwrite workflow.

## Maintain an installation

```bash
# Report upstream branch heads; do not approve or install new code.
./scripts/library.sh check-updates

# Apply versions already reviewed and committed in this library.
./scripts/library.sh update --scope project --target .cache/demo --profile sysadmin --dry-run
./scripts/library.sh update --scope project --target .cache/demo --profile sysadmin

# Remove only selected, unchanged files owned by this library.
./scripts/library.sh uninstall --scope project --target .cache/demo --profile sysadmin --dry-run
./scripts/library.sh uninstall --scope project --target .cache/demo --profile sysadmin
```

See [installation and usage](docs/usage.md) for workflows and examples, [contribution and update review](docs/contributing.md) for adding sources, and [architecture](docs/architecture.md) for component boundaries. MCP templates live separately in `integrations/mcp/`; review their documentation before enabling any connection.

## Verification and safety

```bash
python3 -m unittest discover -s tests -v
./scripts/library.sh validate
```

[Verification results](docs/verification.md) distinguish static checks, isolated Codex discovery, and untested authenticated integrations. A successful format check does not prove that a skill workflow or remote server works in your environment.

No secrets belong in this repository. Review external scripts before execution, prefer read-only diagnostics, use the smallest required permissions, and obtain explicit authorization before destructive operations. Instructions express behavior; they do not replace sandbox or tool permissions.

Third-party components retain their own licenses. Review `catalog/`, `sources/` and the original license files before redistribution or adaptation; approval here is a bounded review, not a guarantee of security.
