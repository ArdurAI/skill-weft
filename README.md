# SkillWeft

SkillWeft is a portable skill-management layer for AI tools. It keeps skills in one place, indexes them, suggests the right skill for a task, and emits compact context packs that Codex, Claude, Gemini, Kimi, Grok, Cursor, Hermes, and other agents can consume without loading every skill all the time.

## Problem

AI tools benefit from procedural skills, but each tool usually has its own local prompt/skill setup. That creates duplication, stale instructions, and context bloat.

## MVP goal

Build a local-first CLI/service that:

1. Stores skill documents in a common registry.
2. Indexes metadata, tags, descriptions, and content.
3. Suggests relevant skills for a natural-language task.
4. Emits a compact context pack with only the selected skills.
5. Checks for stale or low-quality skills and recommends updates.

## Quick start

```bash
python -m skillweft.cli add examples/skills/python-debugging.md --registry .skillweft/skills
python -m skillweft.cli suggest "debug a failing pytest test" --registry .skillweft/skills
python -m skillweft.cli pack "debug a failing pytest test" --registry .skillweft/skills --max-skills 2 --budget 2000
```

## Phase 1 preflight router

SkillWeft can now detect installed AI-agent CLIs and build dry-run launch plans that include only the selected skill context:

```bash
PYTHONPATH=src python3 -m skillweft.cli doctor
PYTHONPATH=src python3 -m skillweft.cli run claude "debug pytest" --registry examples/skills --dry-run
PYTHONPATH=src python3 -m skillweft.cli run codex "debug pytest" --registry examples/skills --dry-run
PYTHONPATH=src python3 -m skillweft.cli run gemini "debug pytest" --registry examples/skills --dry-run
```

Supported Phase 1 adapters:

- Claude Code
- Codex CLI
- Gemini CLI
- Hermes Agent
- Cursor CLI / `agent`

## Current status

Phase 1 working prototype: local registry + keyword suggestions + budget-aware context packs + `doctor` + dry-run launch adapters for Claude Code, Codex CLI, Gemini CLI, Hermes, and Cursor.

## Real-world tests

The normal test suite includes skipped-by-default Olla API real-world tests. They use the real local skill registry and an Olla/OpenAI-compatible chat-completions API as an external judge for routing quality.

```bash
# Unit/offline suite; live Olla tests are skipped unless enabled.
PYTHONPATH=src python3 -m unittest discover -s tests

# Live Olla test run, only after setting a key intentionally.
export OLLA_API_KEY='***'
export SKILLWEFT_RUN_OLLA_REAL_WORLD=1
PYTHONPATH=src python3 -m unittest tests.test_olla_api_real_world -v
```

See `docs/testing/olla-real-world-tests.md` for all environment variables.
