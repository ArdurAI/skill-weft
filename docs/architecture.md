# SkillHub Architecture

## Components

1. Skill Registry
   - Stores canonical Markdown skill files.
   - Reads YAML-like frontmatter when present.
   - Normalizes name, description, tags, and body.

2. Indexer
   - Builds a lightweight searchable representation.
   - MVP uses deterministic keyword scoring.
   - Future: embeddings, usage telemetry, recency, success rates.

3. Router
   - Accepts a task description.
   - Scores skills.
   - Returns top candidates with reasons.

4. Context Packer
   - Converts selected skills into a compact prompt block.
   - Supports text and JSON output.
   - Future: per-tool adapters.

5. Maintenance Engine
   - Checks skill quality and staleness.
   - Flags missing descriptions, tags, examples, verification steps, and very old skills.

## Future adapters

- Codex: AGENTS.md/context injection or CLI wrapper.
- Claude Code: skill/context directory bridge.
- Cursor: project rules / context files.
- Gemini CLI: prompt/context wrapper.
- Hermes: native skill registry bridge.
- API mode: HTTP endpoint for any external agent.
