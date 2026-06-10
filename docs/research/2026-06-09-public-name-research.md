# Public repository naming research

Date: 2026-06-09

Goal: choose a distinctive public repository/project name for the centralized AI skill registry, router, MCP bridge, and adapter system.

## Selected name

**SkillWeft**

Repository slug:

```text
skill-weft
```

Why it fits:

- "Weft" is the crosswise thread in weaving. The metaphor fits a system that weaves skills into many AI tools without dumping every skill into context.
- It is short, pronounceable, and related to the product function without being overly generic.
- It keeps "skill" in the name, making the purpose clear.
- It works as a CLI/package name: `skillweft`.

## Collision checks performed

Checked exact availability for top candidates across:

- GitHub public repository name search
- npm package registry
- PyPI package registry
- crates.io registry

For `skill-weft` and `skillweft`, exact checks on 2026-06-09 returned:

| Name | GitHub exact repo | npm | PyPI | crates.io |
|---|---:|---:|---:|---:|
| `skill-weft` | none found | 404/not found | 404/not found | 404/not found |
| `skillweft` | none found | 404/not found | 404/not found | 404/not found |

## Other viable names found collision-free in exact checks

- `praxi-mux` / `praximux`
- `context-quiver`
- `lore-mux` / `loremux`
- `skill-loomlet` / `skillloomlet`
- `agent-praxis` / `agentpraxis`
- `skill-lattice` / `skilllattice`
- `context-lattice` / `contextlattice`
- `skill-orbit` / `skillorbit`
- `skill-ferry` / `skillferry`
- `skill-capsule` / `skillcapsule`
- `skill-compass` / `skillcompass`

## Names rejected due to collisions

- `skillmux` — exact GitHub, npm, and PyPI collisions found.
- `skill-quiver` — exact GitHub collisions found.
- `skill-sieve` / `skillsieve` — exact GitHub collisions found.
- `skilldock` — npm and PyPI collisions found.
- `skill-os` / `skillos` — npm or PyPI collision found.

## Naming decision

Use:

```text
ArdurAI/skill-weft
```

Public name:

```text
SkillWeft
```

Python package/project name:

```text
skill-weft
```

CLI command:

```text
skillweft
```

Compatibility alias:

```text
skillhub
```

The compatibility alias is useful because the initial prototype used the working name SkillHub, but the public repo/project should use the more distinctive SkillWeft name.
