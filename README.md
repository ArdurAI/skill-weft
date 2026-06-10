# SkillHub

SkillHub is a portable skill-management layer for AI tools. It keeps skills in one place, indexes them, suggests the right skill for a task, and emits compact context packs that Codex, Claude, Gemini, Kimi, Grok, Cursor, Hermes, and other agents can consume without loading every skill all the time.

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
python -m skillhub.cli add examples/skills/python-debugging.md --registry .skillhub/skills
python -m skillhub.cli suggest "debug a failing pytest test" --registry .skillhub/skills
python -m skillhub.cli pack "debug a failing pytest test" --registry .skillhub/skills --max-skills 2
```

## Current status

Initial working prototype: local registry + keyword-based suggestions + JSON/text context packs.
