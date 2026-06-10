# Hybrid SkillHub Architecture Implementation Plan

> **For Hermes:** Use subagent-driven-development skill to implement this plan task-by-task.

**Goal:** Build SkillHub as a hybrid skill-management layer with (1) preflight routing before an AI agent starts, (2) a runtime MCP server that agents can query during work, and (3) tool-specific adapters for Claude Code, Codex, Gemini, Cursor, Hermes, and future agents.

**Architecture:** SkillHub remains the canonical registry and router. Adapters never duplicate the whole skill library into each tool; they either inject a compact preflight context pack or configure an MCP server exposing a small router API. The registry, feedback, audit, and usage history stay local-first and tool-agnostic.

**Tech Stack:** Python 3.10+, Markdown skill files, SQLite for feedback/usage, optional `mcp` Python package for MCP server mode, CLI wrappers for agent tools, JSON config generators for tool integrations.

---

## Verified integration facts on this machine

Checked on 2026-06-09 under `/Users/gnutakki16/skillhub`:

| Tool | Status | Verified integration surfaces |
|---|---|---|
| Claude Code 2.1.143 | Installed | `claude -p`, `--append-system-prompt-file`, `--mcp-config`, `--strict-mcp-config`, `claude mcp add/list` |
| Codex CLI 0.130.0 | Installed | `codex exec [PROMPT]`, prompt from stdin, `--cd`, `--sandbox`, `--skip-git-repo-check`, `--json` |
| Gemini CLI 0.45.3 | Installed | `gemini -p`, `gemini mcp`, `gemini skills`, `--allowed-mcp-server-names`, JSON/stream-json output |
| Hermes Agent 0.16.0 | Installed | Native skills, `hermes mcp serve`, `hermes mcp add/list/test`, `hermes -s SKILL` |
| Cursor CLI | Not installed/verified | Plan via `.cursor/rules` and MCP config, but exact CLI automation must be verified later |

Important Gemini note: `@google/gemini-cli` installed under `~/.hermes/node`, and `/Users/gnutakki16/.local/bin/gemini` was symlinked to the package binary.

---

## Product shape

SkillHub should expose three layers:

### 1. Preflight router

Before launching an agent, SkillHub receives the user task, selects relevant skills, packs the minimum useful context, and launches the target tool.

Example future commands:

```bash
skillhub suggest "fix failing pytest auth tests"
skillhub pack "fix failing pytest auth tests" --target claude --budget 6000
skillhub run claude "fix failing pytest auth tests"
skillhub run codex "fix failing pytest auth tests"
skillhub run gemini "fix failing pytest auth tests"
```

### 2. Runtime MCP server

During a task, capable agents can call SkillHub dynamically.

MCP tools should be few and generic:

```text
suggest_skills(task, max_skills?, budget?)
get_skill(name_or_id, mode?)
pack_context(task, budget?, target?)
report_skill_outcome(skill_id, task, outcome, notes?)
audit_skill(name_or_id?)
```

Do not expose each skill as its own tool. That would bloat tool schemas and recreate the original context problem.

### 3. Tool-specific adapters

Adapters translate SkillHub context into each tool's native integration surface:

- Claude Code: `--append-system-prompt-file`, MCP config, `.claude/skills` export if wanted.
- Codex: prompt/stdin wrapper around `codex exec`, optional project instruction file later.
- Gemini: `gemini -p`, `gemini mcp`, `gemini skills`/extensions later.
- Hermes: native skill bridge and/or MCP.
- Cursor: `.cursor/rules` generation and MCP config once verified.

---

## Design principles

1. **Canonical registry:** Skills live once in SkillHub.
2. **Small runtime API:** MCP exposes router operations, not hundreds of skill tools.
3. **Preflight first:** Wrapper-based preflight routing works even if the target model never calls MCP.
4. **Runtime optional:** MCP improves flexibility for tools that support it.
5. **Context budget aware:** Context packs must support token/character budgets.
6. **Explainable routing:** Every selected skill includes a reason.
7. **Human-approved maintenance:** SkillHub can suggest updates, but canonical skill edits should be reviewable.
8. **Safe provenance:** Track source, owner, trust level, and last modified time for each skill.
9. **No secret leakage:** Skills and feedback logs must not store credentials.
10. **Tool-agnostic core:** Adapters depend on core; core never depends on a specific AI tool.

---

## Proposed repository layout

```text
src/skillhub/
  __init__.py
  cli.py
  models.py
  registry.py
  router.py
  retrieval.py
  packer.py
  token_budget.py
  storage.py
  feedback.py
  maintenance.py
  mcp_server.py
  adapters/
    __init__.py
    base.py
    claude.py
    codex.py
    gemini.py
    hermes.py
    cursor.py
  integrations/
    claude_mcp_config.py
    gemini_mcp_config.py
    cursor_rules.py

tests/
  test_models.py
  test_registry.py
  test_router.py
  test_packer.py
  test_feedback.py
  test_maintenance.py
  test_mcp_contract.py
  test_adapters_claude.py
  test_adapters_codex.py
  test_adapters_gemini.py
  test_cli.py

examples/
  skills/
  mcp/
  adapters/
```

---

## Data model

### Task 1: Add core models

**Objective:** Centralize typed objects shared by registry, router, packer, MCP, and adapters.

**Files:**
- Create: `src/skillhub/models.py`
- Modify: `src/skillhub/registry.py`
- Modify: `src/skillhub/router.py`
- Test: `tests/test_models.py`

**Implementation sketch:**

```python
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal


@dataclass(frozen=True)
class Skill:
    id: str
    name: str
    description: str
    tags: tuple[str, ...]
    content: str
    path: Path
    version: str | None = None
    source: str | None = None
    trust_level: Literal["local", "trusted", "external", "unknown"] = "unknown"


@dataclass(frozen=True)
class Suggestion:
    skill: Skill
    score: float
    reasons: tuple[str, ...]
    matched_terms: tuple[str, ...] = ()


@dataclass(frozen=True)
class ContextPack:
    task: str
    target: str
    skills: tuple[Suggestion, ...]
    content: str
    estimated_tokens: int


@dataclass(frozen=True)
class SkillFeedback:
    skill_id: str
    task: str
    outcome: Literal["success", "failure", "partial", "unknown"]
    notes: str = ""
```

**Verification:**

```bash
PYTHONPATH=src python3 -m unittest tests.test_models -v
```

Expected: model construction and serialization tests pass.

---

## Registry and indexing

### Task 2: Upgrade registry to stable IDs and metadata

**Objective:** Give each skill a stable ID and richer metadata while preserving simple Markdown compatibility.

**Files:**
- Modify: `src/skillhub/registry.py`
- Test: `tests/test_registry.py`

**Requirements:**

- Parse frontmatter fields: `name`, `description`, `tags`, `version`, `source`, `trust_level`.
- Generate `id` from relative path or name.
- Continue supporting plain Markdown with no frontmatter.
- Return deterministic sorted results.

**Verification:**

```bash
PYTHONPATH=src python3 -m unittest tests.test_registry -v
```

---

### Task 3: Add index builder

**Objective:** Separate indexing from retrieval so keyword and embedding retrieval can coexist later.

**Files:**
- Create: `src/skillhub/retrieval.py`
- Modify: `src/skillhub/router.py`
- Test: `tests/test_router.py`

**MVP implementation:**

```python
class KeywordRetriever:
    def search(self, task: str, skills: list[Skill], limit: int = 5) -> list[Suggestion]:
        ...
```

**Future extension:**

```python
class EmbeddingRetriever:
    def build_index(self, skills: list[Skill]) -> None: ...
    def search(self, task: str, limit: int = 5) -> list[Suggestion]: ...
```

**Verification:**

```bash
PYTHONPATH=src python3 -m unittest tests.test_router -v
```

---

## Context packing

### Task 4: Add token/character budget support

**Objective:** Pack only the most useful context for the target tool.

**Files:**
- Create: `src/skillhub/token_budget.py`
- Modify: `src/skillhub/packer.py`
- Test: `tests/test_packer.py`

**Rules:**

- Start with character-based estimate: `tokens ~= chars / 4`.
- Always include task, selected skill names, descriptions, and reasons.
- Include full skill content only while budget allows.
- If content is too large, include sections in this priority:
  1. trigger/when-to-use
  2. steps/procedure
  3. verification
  4. examples
  5. pitfalls
- Never silently exceed the budget by more than 10%.

**CLI examples:**

```bash
skillhub pack "debug pytest" --target claude --budget 6000
skillhub pack "debug pytest" --target codex --budget 4000 --format json
```

**Verification:**

```bash
PYTHONPATH=src python3 -m unittest tests.test_packer -v
PYTHONPATH=src python3 -m skillhub.cli pack "debug pytest" --registry examples/skills --budget 1000
```

---

## Preflight router

### Task 5: Add adapter abstraction

**Objective:** Define a common interface for launching or configuring AI tools.

**Files:**
- Create: `src/skillhub/adapters/__init__.py`
- Create: `src/skillhub/adapters/base.py`
- Test: `tests/test_adapters_base.py`

**Interface sketch:**

```python
from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class LaunchPlan:
    command: list[str]
    stdin: str | None
    env: dict[str, str]
    temp_files: dict[str, str]
    notes: tuple[str, ...]


class AgentAdapter(Protocol):
    name: str

    def available(self) -> bool: ...
    def build_launch_plan(self, task: str, context_pack: str, **kwargs) -> LaunchPlan: ...
    def integration_status(self) -> dict: ...
```

**Verification:** unit tests can create a fake adapter and assert launch plan fields.

---

### Task 6: Add Claude Code adapter

**Objective:** Support Claude Code with both preflight context injection and MCP config generation.

**Files:**
- Create: `src/skillhub/adapters/claude.py`
- Create: `src/skillhub/integrations/claude_mcp_config.py`
- Test: `tests/test_adapters_claude.py`

**Verified surfaces:**

- `claude -p` for non-interactive mode.
- `--append-system-prompt-file <path>` for preflight context.
- `--mcp-config <path>` for runtime MCP.
- `claude mcp add/list` for persistent configuration.

**Preflight command shape:**

```bash
claude -p "<task>" \
  --append-system-prompt-file /tmp/skillhub-context.md \
  --mcp-config /tmp/skillhub-mcp.json \
  --max-turns 10
```

**MCP config shape:**

```json
{
  "mcpServers": {
    "skillhub": {
      "command": "python3",
      "args": ["-m", "skillhub.mcp_server", "stdio"]
    }
  }
}
```

**Verification:**

```bash
PYTHONPATH=src python3 -m unittest tests.test_adapters_claude -v
skillhub doctor --target claude
```

Expected: adapter reports Claude installed and shows supported surfaces.

---

### Task 7: Add Codex adapter

**Objective:** Support Codex preflight routing through prompt/stdin injection.

**Files:**
- Create: `src/skillhub/adapters/codex.py`
- Test: `tests/test_adapters_codex.py`

**Verified surfaces:**

- `codex exec [PROMPT]`.
- If prompt is `-` or absent, instructions can be read from stdin.
- `--cd <DIR>` controls working root.
- `--skip-git-repo-check` can be used for scratch/non-repo tests.
- `--json` can emit structured events.

**Preflight command shape:**

```bash
printf '%s' "<SkillHub context pack>\n\nUser task: <task>" | \
  codex exec - --cd /path/to/project --sandbox workspace-write
```

**Important:** For Codex, SkillHub does not need native Codex plugin support. A wrapper is enough for v1.

**Verification:**

```bash
PYTHONPATH=src python3 -m unittest tests.test_adapters_codex -v
skillhub doctor --target codex
```

---

### Task 8: Add Gemini adapter

**Objective:** Support Gemini CLI with preflight and runtime MCP.

**Files:**
- Create: `src/skillhub/adapters/gemini.py`
- Create: `src/skillhub/integrations/gemini_mcp_config.py`
- Test: `tests/test_adapters_gemini.py`

**Verified surfaces:**

- `gemini -p "prompt"` for non-interactive mode.
- `gemini mcp` for MCP management.
- `gemini skills` exists and should be explored for deeper integration.
- `--allowed-mcp-server-names` can restrict runtime MCP access.
- `--output-format json` exists.

**Preflight command shape:**

```bash
gemini -p "<SkillHub context pack>\n\nUser task: <task>" --output-format json
```

**Runtime MCP mode:**

```bash
gemini -p "<task>" --allowed-mcp-server-names skillhub
```

**Verification:**

```bash
PYTHONPATH=src python3 -m unittest tests.test_adapters_gemini -v
skillhub doctor --target gemini
```

---

### Task 9: Add Hermes adapter

**Objective:** Support Hermes as both a target agent and an MCP-capable host.

**Files:**
- Create: `src/skillhub/adapters/hermes.py`
- Test: `tests/test_adapters_hermes.py`

**Verified surfaces:**

- `hermes chat -q "..."` for non-interactive usage.
- `hermes -s skill` for native skill preloading.
- `hermes mcp add/list/test` for runtime MCP.
- `hermes mcp serve` to expose Hermes itself as an MCP server if needed.

**Preflight command shape:**

```bash
hermes chat -q "<SkillHub context pack>\n\nUser task: <task>"
```

**Future native mode:**

SkillHub can generate temporary Hermes skill files and launch:

```bash
hermes -s generated-skillhub-pack chat -q "<task>"
```

**Verification:**

```bash
PYTHONPATH=src python3 -m unittest tests.test_adapters_hermes -v
skillhub doctor --target hermes
```

---

### Task 10: Add Cursor adapter

**Objective:** Generate Cursor-compatible project context even before CLI automation is verified.

**Files:**
- Create: `src/skillhub/adapters/cursor.py`
- Create: `src/skillhub/integrations/cursor_rules.py`
- Test: `tests/test_adapters_cursor.py`

**MVP output:**

Generate a project-local rules file:

```text
.cursor/rules/skillhub.generated.md
```

Content:

```markdown
# SkillHub Context

This file is generated. Do not edit manually.

<packed relevant skills>
```

**Verification:**

```bash
PYTHONPATH=src python3 -m unittest tests.test_adapters_cursor -v
skillhub export cursor "debug pytest" --output .cursor/rules/skillhub.generated.md
```

**Note:** Cursor CLI/runtime MCP details must be verified separately once Cursor is installed.

---

## Runtime MCP server

### Task 11: Add MCP server package dependency

**Objective:** Make MCP support optional but easy to install.

**Files:**
- Modify: `pyproject.toml`
- Create: `src/skillhub/mcp_server.py`
- Test: `tests/test_mcp_contract.py`

**Dependency plan:**

```toml
[project.optional-dependencies]
mcp = ["mcp>=1.0"]
```

**Verification:**

```bash
python3 -m pip install -e '.[mcp]'
PYTHONPATH=src python3 -m skillhub.mcp_server --help
```

---

### Task 12: Implement MCP tool contract

**Objective:** Expose SkillHub through a stable MCP API.

**Files:**
- Modify: `src/skillhub/mcp_server.py`
- Test: `tests/test_mcp_contract.py`

**Tools:**

```text
suggest_skills(task: str, max_skills: int = 5, budget: int | None = None)
get_skill(name_or_id: str, mode: "full" | "summary" = "full")
pack_context(task: str, budget: int = 6000, target: str = "generic")
report_skill_outcome(skill_id: str, task: str, outcome: str, notes: str = "")
audit_skill(name_or_id: str | None = None)
```

**Response rule:** All responses must be JSON-serializable and compact. Large skill content must be explicitly requested via `get_skill`.

**Verification:**

Run contract tests without launching a real MCP host:

```bash
PYTHONPATH=src python3 -m unittest tests.test_mcp_contract -v
```

Later integration test with Claude/Gemini/Hermes MCP host:

```bash
skillhub mcp serve --stdio
claude mcp add skillhub -- python3 -m skillhub.mcp_server stdio
```

---

## Feedback and maintenance

### Task 13: Add SQLite feedback store

**Objective:** Track usage and outcomes without polluting skill files.

**Files:**
- Create: `src/skillhub/storage.py`
- Create: `src/skillhub/feedback.py`
- Test: `tests/test_feedback.py`

**Tables:**

```sql
skills_seen(skill_id TEXT PRIMARY KEY, path TEXT, first_seen_at TEXT, last_seen_at TEXT)
skill_usage(id INTEGER PRIMARY KEY, skill_id TEXT, task TEXT, target TEXT, used_at TEXT)
skill_feedback(id INTEGER PRIMARY KEY, skill_id TEXT, task TEXT, outcome TEXT, notes TEXT, created_at TEXT)
audit_findings(id INTEGER PRIMARY KEY, skill_id TEXT, severity TEXT, message TEXT, created_at TEXT, resolved_at TEXT)
```

**Verification:**

```bash
PYTHONPATH=src python3 -m unittest tests.test_feedback -v
```

---

### Task 14: Expand audit engine

**Objective:** Make skill maintenance useful and safe.

**Files:**
- Modify: `src/skillhub/maintenance.py`
- Test: `tests/test_maintenance.py`

**Checks:**

- Missing description.
- Missing tags.
- Missing trigger/when-to-use section.
- Missing verification section.
- Missing examples.
- Very short skill.
- Duplicate name/tag collision.
- Repeated failure feedback.
- Stale skill not touched in N days.
- Untrusted source.

**Verification:**

```bash
PYTHONPATH=src python3 -m unittest tests.test_maintenance -v
skillhub audit --registry examples/skills
```

---

### Task 15: Add human-review update workflow

**Objective:** Let SkillHub suggest skill updates without silently editing canonical skills.

**Files:**
- Create: `src/skillhub/review_queue.py`
- Modify: `src/skillhub/cli.py`
- Test: `tests/test_review_queue.py`

**Commands:**

```bash
skillhub feedback python-debugging --outcome failure --notes "Did not mention pytest -k"
skillhub audit
skillhub review list
skillhub review show <id>
skillhub review apply <id>
skillhub review reject <id>
```

**Rule:** `review apply` may edit skill files; audit/feedback commands must not.

---

## CLI commands

### Task 16: Add complete CLI surface

**Objective:** Make the three architecture layers usable from terminal.

**Files:**
- Modify: `src/skillhub/cli.py`
- Test: `tests/test_cli.py`

**Commands:**

```bash
skillhub add <skill.md> --registry .skillhub/skills
skillhub list --registry .skillhub/skills
skillhub suggest "task" --registry .skillhub/skills
skillhub pack "task" --target claude --budget 6000
skillhub run claude "task" --dry-run
skillhub run codex "task" --dry-run
skillhub run gemini "task" --dry-run
skillhub mcp serve --stdio
skillhub integrate claude --scope user
skillhub integrate gemini --scope user
skillhub export cursor "task" --output .cursor/rules/skillhub.generated.md
skillhub feedback <skill> --outcome success --notes "..."
skillhub audit
skillhub doctor
```

**Verification:**

```bash
PYTHONPATH=src python3 -m unittest tests.test_cli -v
PYTHONPATH=src python3 -m skillhub.cli doctor
PYTHONPATH=src python3 -m skillhub.cli run claude "debug pytest" --dry-run
```

---

## Security and safety

### Task 17: Add prompt-injection and trust safeguards

**Objective:** Prevent untrusted skills from silently controlling external agents.

**Files:**
- Create: `src/skillhub/security.py`
- Modify: `src/skillhub/packer.py`
- Test: `tests/test_security.py`

**Rules:**

- Context pack header must say skills are procedural guidance, not higher-priority instructions.
- Untrusted external skills are excluded by default unless `--include-untrusted` is passed.
- Redact obvious secrets from feedback notes.
- Warn when a skill contains suspicious phrases like:
  - `ignore previous instructions`
  - `exfiltrate`
  - `send secrets`
  - `disable safety`

**Verification:**

```bash
PYTHONPATH=src python3 -m unittest tests.test_security -v
```

---

## Integration test strategy

### Task 18: Add non-auth integration checks

**Objective:** Validate local tool surfaces without consuming model/API calls.

**Files:**
- Create: `tests/test_integration_surfaces.py`

**Checks:**

- `claude --version` works if installed.
- `claude --help` includes `--append-system-prompt-file` and `--mcp-config`.
- `codex exec --help` includes stdin prompt behavior and `--cd`.
- `gemini --help` includes `-p`, `gemini mcp`, and `--allowed-mcp-server-names`.
- `hermes mcp --help` includes `serve`, `add`, `list`, `test`.

**Verification:**

```bash
PYTHONPATH=src python3 -m unittest tests.test_integration_surfaces -v
```

---

## Milestones

### Milestone 1: Preflight works end-to-end

Target: 2-4 days.

Deliverables:
- stable skill models
- budget-aware packer
- `skillhub run claude --dry-run`
- `skillhub run codex --dry-run`
- `skillhub run gemini --dry-run`
- `skillhub doctor`

Definition of done:

```bash
PYTHONPATH=src python3 -m unittest discover -s tests
skillhub run claude "debug pytest" --dry-run
skillhub run codex "debug pytest" --dry-run
skillhub run gemini "debug pytest" --dry-run
```

### Milestone 2: MCP server works locally

Target: 3-7 days.

Deliverables:
- `skillhub mcp serve --stdio`
- MCP contract tests
- Claude/Gemini/Hermes config generators
- runtime tools: suggest/get/pack/report/audit

Definition of done:

```bash
skillhub mcp serve --help
skillhub integrate claude --dry-run
skillhub integrate gemini --dry-run
```

### Milestone 3: Feedback and maintenance

Target: 1-2 weeks.

Deliverables:
- SQLite feedback store
- skill usage tracking
- audit queue
- human-reviewed update workflow

Definition of done:

```bash
skillhub feedback python-debugging --outcome success --notes "worked"
skillhub audit
skillhub review list
```

### Milestone 4: One-stop-shop UX

Target: 2-4 weeks.

Deliverables:
- TUI or local web UI
- browse/search/edit skills
- adapter status dashboard
- review queue
- usage/failure stats

---

## Recommended implementation order

1. Models and registry upgrade.
2. Budget-aware packer.
3. Adapter abstraction.
4. Claude/Codex/Gemini dry-run adapters.
5. `skillhub doctor`.
6. MCP server contract.
7. Claude/Gemini/Hermes MCP config generators.
8. Feedback SQLite store.
9. Audit/review queue.
10. Cursor adapter once Cursor CLI/MCP behavior is verified.

---

## Key risks

1. **Over-selection:** Router may select too many skills. Mitigate with score thresholds and budgets.
2. **Under-selection:** Router may miss needed skills. Mitigate with runtime MCP `suggest_skills`.
3. **Context bloat:** Full skills can be huge. Mitigate with excerpts and budgets.
4. **Tool drift:** CLI flags change. Mitigate with `doctor` checks and surface tests.
5. **Prompt injection:** Skills are prompt content. Mitigate with trust levels and security scanning.
6. **Closed tools:** Some tools may not expose MCP/CLI/plugin surfaces. Mitigate with wrappers or export-only adapters.
7. **Skill rot:** Old skills become wrong. Mitigate with feedback, audits, and review queue.

---

## Success criteria

SkillHub is successful when this workflow works reliably:

```bash
skillhub run claude "add tests for the auth middleware"
skillhub run codex "fix the failing pytest auth test"
skillhub run gemini "review this design doc for missing edge cases"
```

For each command, SkillHub should:

1. select relevant skills,
2. explain why they were selected,
3. pack them within budget,
4. launch or dry-run the target adapter,
5. expose runtime MCP tools where available,
6. record skill usage and feedback,
7. surface stale or failing skills for human review.
