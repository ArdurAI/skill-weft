# Olla real-world test harness

SkillWeft includes an opt-in real-world test suite that uses an Olla/OpenAI-compatible chat-completions API as an external judge for routing quality.

The tests are safe by default:

- They do not run paid/network calls during the normal unit suite unless explicitly enabled.
- They require `OLLA_API_KEY`.
- They also require `SKILLWEFT_RUN_OLLA_REAL_WORLD=1` so a key in the environment does not accidentally spend credits.
- The API key is never printed by the tests.

## Environment variables

Required:

```bash
export OLLA_API_KEY='...'
export SKILLWEFT_RUN_OLLA_REAL_WORLD=1
```

Optional:

```bash
# Default: https://api.olla.ai/v1
export OLLA_BASE_URL='https://api.olla.ai/v1'

# Default: gpt-4o-mini
export OLLA_MODEL='gpt-4o-mini'

# Default: ~/.hermes/skills
export SKILLWEFT_REAL_REGISTRY='/Users/gnutakki16/.hermes/skills'

# Default: 60
export OLLA_TIMEOUT_SECONDS=60
```

`OLLA_BASE_URL` should be the API root, not the full endpoint. SkillWeft appends `/chat/completions`.

## Run only Olla real-world tests

```bash
PYTHONPATH=src python3 -m unittest tests.test_olla_api_real_world -v
```

## Run full suite including skipped real-world tests

Without the opt-in env vars, these tests show as skipped:

```bash
PYTHONPATH=src python3 -m unittest discover -s tests -v
```

With the env vars set, they make live API calls:

```bash
export OLLA_API_KEY='...'
export SKILLWEFT_RUN_OLLA_REAL_WORLD=1
PYTHONPATH=src python3 -m unittest discover -s tests -v
```

## What the tests validate

The live Olla judge checks SkillWeft's selected skills/context packs for realistic tasks:

1. GitHub repository creation/push workflow should select `github-workflows`.
2. MCP configuration workflow should select `native-mcp` or `ai-skill-management-systems`.
3. Implementation planning workflow should select `writing-plans` or `plan`.

Each test:

1. Loads the real local skill registry.
2. Runs SkillWeft routing.
3. Builds a budget-limited context pack.
4. Sends the task, selected skills, and context pack to Olla.
5. Requires a strict JSON verdict with `relevant: true` and no unrelated skills.
