# SkillHub user adoption and integration strategy research

Date: 2026-06-09

Goal: identify the best practical way for both non-technical and technical users to incorporate SkillHub into the AI tools they already use.

## Executive recommendation

The best incorporation strategy is not a single integration path. It is a layered product:

1. **Agent Skills package format as the canonical skill artifact**
   - Store skills as folders containing `SKILL.md` plus optional `references/`, `scripts/`, `templates/`, and `assets/`.
   - This aligns SkillHub with the emerging Agent Skills standard instead of inventing a private format.
   - SkillHub should manage, audit, version, route, and sync these packages.

2. **Runtime MCP server as the universal live bridge**
   - Expose only a small router API over MCP:
     - `suggest_skills`
     - `get_skill`
     - `pack_context`
     - `report_skill_outcome`
     - `audit_skill`
   - Do **not** expose every skill as a separate MCP tool. That would bloat the tool schema and recreate the context-bloat problem.

3. **Preflight launcher/wrapper as the reliability layer**
   - Before an agent starts, SkillHub selects relevant skills and injects a compact context pack.
   - This works even if the target agent never decides to call MCP during the session.

4. **One-click/non-technical UX on top**
   - A desktop app or local web UI should detect installed tools and show “Connect Claude”, “Connect Cursor”, “Connect Codex”, “Connect Gemini”, “Connect Hermes”.
   - Under the hood, it runs the same CLI/config/symlink/MCP setup that technical users can run manually.

5. **Team/enterprise mode later**
   - Hosted SkillHub registry + remote HTTP MCP + OAuth/SSO + org skill policies + audit logs.

The product positioning should be:

> SkillHub is the shared skill registry, router, and maintenance layer for AI agents. It stores skills once, makes them available everywhere, and injects only the skills needed for the current task.

## Why this is the best approach

### Agent Skills are becoming a portable packaging layer

Evidence:

- Cursor documents Agent Skills as “an open standard for extending AI agents with specialized capabilities” and says skills are portable, version-controlled, actionable, and progressive.
- Cursor loads skills from `.agents/skills/`, `.cursor/skills/`, `~/.agents/skills/`, and `~/.cursor/skills/`, and also loads compatibility locations `.claude/skills/`, `.codex/skills/`, `~/.claude/skills/`, and `~/.codex/skills/`.
- The MCP docs describe agent skills as portable instruction sets and say a skill ships a `SKILL.md` file plus a `references/` folder that agents read on demand.

Implication for SkillHub:

SkillHub should not treat skills as loose Markdown prompt snippets only. It should treat each skill as a package. The canonical on-disk layout should be compatible with Agent Skills:

```text
skillhub-registry/
  skills/
    python-debugging/
      SKILL.md
      references/
      scripts/
      templates/
      assets/
```

The registry can still import existing Hermes-style skills, Obsidian notes, Honcho Memo content, or plain Markdown, but the exported/native format should be Agent Skills-compatible.

### MCP is the best live integration layer, but not the only layer

Evidence:

- MCP defines a standard way for AI apps to connect to tools, data sources, and workflows.
- The MCP transport spec defines stdio and Streamable HTTP as standard transports; clients should support stdio when possible.
- Claude Code, Codex, Gemini CLI, Cursor, and Hermes all expose MCP integration surfaces.
- Cursor supports stdio, SSE, and Streamable HTTP MCP transports.
- Codex supports MCP in both CLI and IDE extension.
- Gemini CLI discovers MCP tools from `mcpServers` config.
- Hermes has native MCP client/server support.

Implication for SkillHub:

MCP should be the main runtime bridge. However, MCP does not guarantee the model will call the SkillHub tool at the right time. Therefore, MCP must be paired with preflight routing.

Recommended SkillHub MCP tool set:

```text
skillhub_suggest_skills(task, max_skills=5, budget=None)
skillhub_get_skill(name_or_id, mode="summary|full|references")
skillhub_pack_context(task, budget=6000, target="generic")
skillhub_report_skill_outcome(skill_id, task, outcome, notes="")
skillhub_audit_skill(name_or_id=None)
```

Avoid:

```text
mcp_skillhub_python_debugging
mcp_skillhub_kubernetes_review
mcp_skillhub_security_review
...
```

That turns each skill into a separate tool and makes large skill libraries unusable.

### Preflight wrappers solve reliability and non-MCP targets

Evidence:

- Claude Code supports non-interactive print mode and context injection via prompt/system prompt/MCP config flags.
- Codex `exec` accepts prompt input from stdin and has `--cd`, sandbox, config, and JSON options.
- Gemini CLI supports `-p/--prompt` headless mode and appends stdin.
- Cursor CLI supports print mode for scripts and automation.
- Hermes supports `hermes chat -q` and native skill/MCP usage.

Implication for SkillHub:

Every tool that has a CLI can support SkillHub through a wrapper:

```bash
skillhub run claude "fix the failing auth tests"
skillhub run codex "add caching to this service"
skillhub run gemini "review this architecture doc"
skillhub run cursor "refactor the React components"
skillhub run hermes "triage these logs"
```

The wrapper flow:

1. Receive task.
2. Detect target tool.
3. Suggest relevant skills.
4. Pack selected skills within a target-specific budget.
5. Launch the tool with the packed context and optional MCP config.
6. Record usage and feedback.

This is the most reliable technical path and can be hidden behind a non-technical desktop UI.

## User segments and best incorporation paths

### Segment 1: Non-technical individual users

Examples:
- Writers using Claude/ChatGPT/Gemini/Grok.
- Product managers using Cursor/Claude for documents.
- Operators using AI tools but not comfortable editing config files.

Best path:

**SkillHub Desktop / Local Web App with one-click connectors.**

UX:

```text
Welcome to SkillHub

[Import skills] [Connect AI tools] [Try a task]

Detected:
✓ Claude Code
✓ Cursor
✓ Gemini CLI
✓ Codex
✓ Hermes

Connectors:
[Connect Claude] [Connect Cursor] [Connect Gemini] [Connect Codex] [Connect Hermes]
```

Under the hood:

- Starts local SkillHub service.
- Registers MCP servers where possible.
- Links or syncs Agent Skills folders.
- Adds wrappers/shortcuts such as “Ask with Claude + SkillHub”.
- Provides a “Copy context pack” fallback for browser-only tools.

Non-technical UX principles:

- No JSON editing.
- No terminal commands required.
- Clear privacy mode: local-only by default.
- Visual confirmation of what was connected.
- “Test connection” button for every tool.
- “Disconnect” button that reverses changes.
- “What skills will be shared?” preview before each task.

Recommended first implementation:

```text
SkillHub Desktop v0:
- local app at http://localhost:<port>
- setup wizard
- tool detection
- connector status
- task box: “What do you want to do?”
- target picker: Claude / Codex / Gemini / Cursor / Hermes / Copy only
- generated command preview for advanced users
```

Why this is best:

- It hides MCP/config complexity.
- It supports both local-first privacy and one-click use.
- It gives non-technical users a mental model: “SkillHub helps my AI pick the right playbook.”

### Segment 2: Technical individual users

Examples:
- Developers using Codex, Claude Code, Cursor, Gemini CLI, Hermes.
- AI power users with many prompt/skill files.
- People comfortable with terminal and dotfiles.

Best path:

**CLI-first install + integrate command + wrappers.**

Target UX:

```bash
pipx install skillhub
skillhub init
skillhub import ~/.hermes/skills
skillhub integrate --all
skillhub doctor
skillhub run codex "fix failing pytest tests"
```

Core commands:

```bash
skillhub doctor
skillhub integrate claude
skillhub integrate codex
skillhub integrate gemini
skillhub integrate cursor
skillhub integrate hermes
skillhub suggest "task"
skillhub pack "task" --target claude
skillhub run claude "task"
skillhub mcp serve --stdio
```

Why this is best:

- Developers can verify exactly what changed.
- CLI integrates well with shells, CI, git, dotfiles, and coding agents.
- Wrappers make SkillHub useful before every target tool has perfect native integration.

### Segment 3: Development teams

Examples:
- Engineering teams standardizing workflows across Cursor, Claude Code, Codex, Gemini, Hermes.
- Platform teams managing code review, security, deployment, and incident-response skills.

Best path:

**Project-level SkillHub profile + repo-pinned Agent Skills + optional remote MCP.**

Target layout:

```text
repo/
  .skillhub/
    manifest.yaml
    policy.yaml
    lock.json
  .agents/skills/
    debugging/tdd/SKILL.md
    security/review/SKILL.md
    deployment/kubernetes/SKILL.md
  .mcp.json                  # if supported by chosen tools
  .cursor/rules/             # generated rules when needed
  .codex/config.toml         # project-scoped Codex config when trusted
  CLAUDE.md / AGENTS.md      # generated light router instructions when needed
```

Team commands:

```bash
skillhub init --team
skillhub sync --project
skillhub audit --ci
skillhub lock
skillhub doctor --project
```

Team rules:

- Commit skills or a lockfile, not uncontrolled generated blobs.
- Use version-pinned skill packs.
- Use CI to reject skills with missing description, missing verification, or suspicious prompt-injection phrases.
- Keep team-level rules small; route detailed workflows through skills.

Why this is best:

- Teams need reproducibility.
- Project-local skills travel with the repo.
- SkillHub can prevent stale/unsafe skill instructions from silently spreading.

### Segment 4: Enterprise/org users

Examples:
- Companies standardizing AI workflows across many teams.
- Security/compliance-heavy environments.

Best path:

**Hosted/private SkillHub server + remote HTTP MCP + SSO + policy.**

Features:

- Central skill registry.
- SSO/OAuth.
- Signed skill packs.
- Approval workflow for skill updates.
- Org/team/project scopes.
- Audit logs.
- Remote HTTP MCP endpoint.
- Local cache for offline/private use.
- Admin dashboard.

Why this is best:

- Enterprises need auditability and central policy.
- Remote HTTP MCP avoids per-user local server setup.
- Org admins can roll out approved skills with versioning and rollback.

### Segment 5: Agent/tool builders

Examples:
- People building custom agents with LangGraph, OpenAI Agents SDK, DSPy, AutoGen, CrewAI, or internal frameworks.

Best path:

**SkillHub SDK + HTTP API + MCP.**

APIs:

```python
from skillhub import SkillHub

hub = SkillHub(registry="./skills")
pack = hub.pack_context("debug failing auth tests", target="my-agent", budget=4000)
```

HTTP:

```http
POST /suggest
POST /pack
GET /skills/{id}
POST /feedback
GET /audit
```

Why this is best:

- Builders can incorporate skill routing directly in their agent loop.
- SDK/API avoids shelling out.
- MCP remains the compatibility bridge for tools that support it.

## Integration matrix

| Tool/user surface | Non-technical path | Technical path | SkillHub adapter priority |
|---|---|---|---|
| Cursor | One-click connector, `.cursor/skills`, `.agents/skills`, MCP config | `skillhub integrate cursor`, `.cursor/rules`, `mcp.json`, CLI wrapper | Very high |
| Claude Code | One-click connector that runs/records `claude mcp add` and skill sync | `skillhub integrate claude`, `--append-system-prompt-file`, `--mcp-config`, `~/.claude/skills` | Very high |
| Codex | Connector for `codex mcp add`, desktop/IDE config, wrapper | `skillhub integrate codex`, `codex exec` wrapper, `.codex/config.toml`, MCP | Very high |
| Gemini CLI | Connector for `gemini mcp add` and `gemini skills link` | `skillhub integrate gemini`, `gemini -p`, `settings.json`, MCP | High |
| Hermes | Native bridge + MCP + skills import/export | `skillhub integrate hermes`, `hermes mcp add`, native skills sync | High |
| Browser-only Claude/ChatGPT/Grok/Kimi | Copy context pack button; later browser extension | `skillhub pack --target generic | pbcopy` | Medium |
| Custom agents | SDK/API/MCP credentials page | Python/TypeScript SDK, HTTP API, MCP client | High |
| Enterprise tools | Admin connector UI | SSO, remote MCP, policy config | Later |

## Recommended connector behavior by tool

### Cursor

Use three paths:

1. Agent Skills package sync/link:
   - Write/link skills into `.agents/skills/` or `.cursor/skills/`.
   - For global personal skills, use `~/.agents/skills/` or `~/.cursor/skills/`.

2. MCP:
   - Generate `mcp.json` with SkillHub stdio or HTTP server.
   - For non-technical users, provide one-click install/deeplink or marketplace path later.

3. Rules:
   - Generate minimal `.cursor/rules/skillhub.mdc` that tells Cursor when to use SkillHub MCP.
   - Do not dump all skills into rules.

Recommended generated rule:

```mdc
---
description: SkillHub routing policy for selecting relevant skills and workflows
alwaysApply: true
---
Before starting a task that may benefit from procedural knowledge, use the SkillHub MCP server to suggest relevant skills. Load only the selected skills or context pack. Do not load the full skill registry into context.
```

### Claude Code

Use three paths:

1. Preflight:
   - Create temporary context pack file.
   - Launch with `claude -p` and `--append-system-prompt-file` or prompt injection.

2. MCP:
   - `claude mcp add skillhub -- python3 -m skillhub.mcp_server stdio`
   - Or use `--mcp-config` for per-run temporary config.

3. Skills:
   - Export/symlink to `~/.claude/skills/` where supported.

### Codex

Use three paths:

1. MCP:
   - `codex mcp add skillhub -- python3 -m skillhub.mcp_server stdio`
   - Or Streamable HTTP for hosted SkillHub.

2. Preflight:
   - Pipe packed context into `codex exec -`.

3. Config:
   - Generate user/project `.codex/config.toml` entries for `mcp_servers.skillhub`.

Important Codex-specific recommendation:

Codex reads the MCP `instructions` field during initialization and uses it as server-wide guidance. SkillHub should keep the first 512 characters of its MCP instructions self-contained and clear:

```text
SkillHub suggests and packs procedural skills for the current task. Call suggest_skills before complex work, then get_skill or pack_context for only the selected skills. Do not request the full registry unless the user explicitly asks.
```

### Gemini CLI

Use three paths:

1. Skills link:
   - `gemini skills link <skillhub-skill-dir>` for live updates.

2. MCP:
   - `gemini mcp add skillhub python3 -m skillhub.mcp_server stdio`
   - Or write `mcpServers` into settings.

3. Preflight:
   - `gemini -p "<packed context>\n\nUser task: ..."`

### Hermes

Use three paths:

1. Native import/export to Hermes skills.
2. MCP:
   - `hermes mcp add skillhub --command python3 --args ...`
3. Preflight:
   - `hermes chat -q "<packed context>\n\nUser task: ..."`

Because Hermes already has a skill system and MCP, this should be one of the easiest integrations.

## Best product packaging

### Package 1: SkillHub Core CLI

Audience: technical users.

Install:

```bash
pipx install skillhub
# or
uv tool install skillhub
```

Primary commands:

```bash
skillhub init
skillhub import
skillhub integrate
skillhub run
skillhub mcp serve
skillhub audit
```

### Package 2: SkillHub Desktop / Local App

Audience: non-technical and mixed users.

Implementation options:

- Tauri/Electron app wrapping the Python/Node local service.
- Or local web app launched by `skillhub app`.
- Bundle a small runtime so users do not install Python manually.

Key screens:

1. Skill library
2. Integrations/connectors
3. Task launcher
4. Review suggested skill updates
5. Privacy/security settings

### Package 3: SkillHub MCP Server

Audience: every MCP-capable AI tool.

Modes:

```bash
skillhub mcp serve --stdio
skillhub mcp serve --http --port 8123
```

### Package 4: SkillHub Cloud / Team Server

Audience: teams/enterprises.

Features:

- hosted registry
- remote MCP URL
- OAuth/SSO
- team skill packs
- approval workflows
- audit logs
- private deployment option

### Package 5: Browser/clipboard fallback

Audience: users of tools without CLI/MCP/plugin support.

Features:

- Copy context pack to clipboard.
- Browser extension later.
- “Paste this at the start of your chat” instructions.

This is not the primary strategy because it is brittle, but it makes SkillHub usable with Grok, Kimi web UI, ChatGPT web UI, and other closed surfaces.

## Adoption funnel

### v0: Developer-first proof

Deliver:

```bash
skillhub suggest "task"
skillhub pack "task"
skillhub run claude "task" --dry-run
skillhub run codex "task" --dry-run
skillhub run gemini "task" --dry-run
skillhub mcp serve --stdio
```

Success metric:

- Developers can see exactly which skills would be used and launch an AI tool with compact context.

### v1: One-command setup

Deliver:

```bash
skillhub integrate --all
skillhub doctor
```

Success metric:

- Tool detection and integration status are clear.
- User can run one task through at least Claude, Codex, Gemini, Cursor, and Hermes where installed.

### v2: Non-technical desktop

Deliver:

- Tool detection UI.
- One-click connect/disconnect.
- “Ask with SkillHub” launcher.
- Context pack preview.
- Skill update review queue.

Success metric:

- A user who never edits JSON can connect Cursor/Claude/Gemini/Codex and run a task.

### v3: Team mode

Deliver:

- `.skillhub/manifest.yaml`
- team skill packs
- policy checks
- CI audit
- shared remote MCP

Success metric:

- A team can commit approved skills and enforce standards across different AI tools.

## What we should build first

The best immediate build order is:

1. **Make SkillHub skills Agent Skills-compatible**
   - Convert examples to folder-based `SKILL.md` packages.
   - Add import/export from Hermes-style skills.

2. **Add `skillhub integrate --dry-run`**
   - Show exactly what would be changed for Claude, Codex, Gemini, Cursor, Hermes.

3. **Add real integrators for installed tools**
   - Claude: MCP + preflight.
   - Codex: MCP + preflight.
   - Gemini: MCP + skills link + preflight.
   - Cursor: `.agents/skills`/`.cursor/skills`, `.cursor/rules`, MCP config.
   - Hermes: skills + MCP.

4. **Add `skillhub run <tool>` wrappers**
   - Make the preflight router useful immediately.

5. **Add MCP server**
   - Runtime live lookup.

6. **Add desktop/local web app**
   - Non-technical onboarding.

## Non-goals for now

Do not start with:

- A browser extension.
- Full hosted cloud service.
- Deep plugin marketplace submissions.
- Trying to modify vendor tools internally.
- Exposing hundreds of skills as hundreds of MCP tools.

Those are later-stage paths.

## Key source evidence collected

Concise evidence excerpts are saved in:

```text
docs/research/2026-06-09-source-excerpts.md
```

Important verified facts:

- MCP is an open standard for connecting AI applications to tools/data/workflows.
- MCP standard transports include stdio and Streamable HTTP; clients should support stdio when possible.
- MCP Agent Skills docs describe skills as portable instruction sets and `SKILL.md` plus `references/` that work with any standard-implementing agent.
- Cursor supports Agent Skills, Rules, MCP, and Headless CLI; its skills docs explicitly load `.agents/skills`, `.cursor/skills`, user-level skill folders, and compatibility locations for Claude/Codex skills.
- Claude Code supports print mode, system prompt/context flags, and MCP config/add commands.
- Codex supports non-interactive `exec`, MCP in both CLI and IDE extension, stdio/Streamable HTTP MCP servers, and shared config via `~/.codex/config.toml` or project `.codex/config.toml`.
- Gemini CLI supports headless prompt mode, MCP, and agent skill install/link commands.
- Hermes supports native skills and MCP client/server commands.

## Final recommendation

For technical users:

```bash
skillhub integrate --all
skillhub run <tool> "task"
skillhub mcp serve --stdio
```

For non-technical users:

```text
Install SkillHub Desktop → Connect AI tools → Ask with SkillHub
```

For teams:

```bash
skillhub init --team
skillhub sync --project
skillhub audit --ci
```

For agent/tool builders:

```text
Use SkillHub MCP, HTTP API, or SDK directly.
```

The first public version should emphasize:

1. Agent Skills-compatible registry.
2. One-command integrations.
3. Preflight wrappers.
4. Runtime MCP server.
5. Local-first privacy.

That combination gives SkillHub a realistic path to work for both non-technical and technical users without waiting for every AI vendor to implement a perfect native plugin system.
