# SkillWeft Vision

SkillWeft is a one-stop skill operating system for AI tools.

## Core idea

Instead of manually loading skills into every AI tool, SkillWeft acts as a shared context router:

- One canonical skill registry.
- Tool adapters for Codex, Claude, Gemini, Kimi, Grok, Cursor, Hermes, and others.
- On-demand skill selection based on the user's task.
- Continuous skill maintenance: detect stale skills, weak examples, missing verification steps, and contradictory instructions.
- Context-budget-aware packing so models receive only the minimum useful procedural context.

## Target users

- Developers using multiple AI coding agents.
- Teams that want reusable workflows across tools.
- Power users who have many skills/prompts but do not want context bloat.

## Design principles

1. Local-first: skills can live on disk and be version-controlled.
2. Portable: Markdown + metadata, no proprietary format lock-in.
3. Explainable routing: every suggestion includes why it was selected.
4. Context efficient: pack only the relevant excerpt/full skill required.
5. Self-healing: stale skills are detected and queued for review.
6. Tool-agnostic: adapters emit formats each AI tool can consume.
