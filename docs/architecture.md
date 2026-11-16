# Architecture and component boundaries

The repository is an offline-first curated collection with a small installer. Bash exposes one entry point and Python 3.11's standard library handles JSON, TOML, hashing and filesystem checks. There is no package service, background process or automatic updater.

| Layer | Responsibility | Authoritative location |
| --- | --- | --- |
| External Skills | Reusable instructions, references and optional scripts | `skills/external/` |
| Upstream agents | Original third-party role definitions | `agents/upstream/` |
| Codex adapters | Standalone TOML accepted by current Codex | `agents/codex/` |
| Catalog | Approved IDs, versions, origins, licenses and review decisions | `catalog/` |
| Source evidence | Repository metadata and original license notices | `sources/` |
| Profiles | Explicit selections of approved catalog IDs | `profiles/` |
| MCP recipes | Optional connections and runtime prerequisites | `integrations/mcp/` |
| Lifecycle | List, validate, install, update, verify and uninstall | `scripts/library.sh` |
| Regression checks | Isolated installer and integrity scenarios | `tests/` |

## Distinct extension mechanisms

A **Skill** is a directory containing `SKILL.md` with a `name` and `description`, optionally accompanied by references and scripts. Codex can select it from the task description, or the operator can invoke it with `$skill-name`. Third-party script files remain inert during installation.

A **custom agent** defines a reusable role for delegated work. Current Codex standalone TOML files require `name`, `description` and `developer_instructions`. Original upstream formats can contain unsupported fields, so adapters preserve the useful instructions while mapping them to the documented schema. They do not impose upstream model names or relax parent permissions.

**AGENTS.md** supplies repository conventions and verification instructions. It is not an installed agent definition or a Skill.

An **MCP server** is an external process or network service exposing tools and data. Merely copying a Skill or agent never supplies those tools. Connections require separate installation, authorization and configuration; recipes remain outside the profile installer.

These boundaries follow the official [Skills documentation](https://developers.openai.com/codex/skills), [custom agent schema](https://developers.openai.com/codex/agent-configuration/subagents), [AGENTS.md guidance](https://developers.openai.com/codex/agent-configuration/agents-md), and [MCP configuration](https://developers.openai.com/codex/mcp), checked on 2026-11-16.

## Version and installation flow

A reviewed upstream commit supplies unchanged source files and license notices. The catalog selects a concrete subset, integrity records detect drift, and profiles reference its component IDs. The installer copies only approved local material into official discovery directories and records ownership in its installation manifest.

`check-updates` only compares remote branch heads. A maintainer must review and commit changed upstream content before `update` can apply it. Installation does not fetch changing branch content.

An existing destination without a matching ownership record is a conflict. Managed content with local changes must be resolved before update or removal. This protects installations created by other tools and preserves operator modifications. Do not edit the state manifest to bypass these checks.

## Scope and compatibility

Project Skills live beneath `.agents/skills/` and project agents beneath `.codex/agents/`. Global Skills use `~/.agents/skills/`; global agent files and the manifest use `CODEX_HOME`, defaulting to `~/.codex`. No global changes are necessary to maintain or test this repository.

The source collection is suitable for future adapters because originals and catalog provenance are separate from Codex installation paths. Compatibility with other clients is not claimed until an adapter and discovery checks exist.

Instruction-level safety supplements client permissions. It cannot block shell execution or remote changes on its own. Configure sandbox and tool permissions in the parent Codex session, review MCP tool exposure, and authorize destructive work explicitly.
