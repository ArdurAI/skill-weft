# SkillHub MVP Implementation Plan

> **For Hermes:** Use subagent-driven-development skill to implement this plan task-by-task.

**Goal:** Build a local-first CLI that stores skills, suggests relevant skills for a task, and emits compact context packs for any AI tool.

**Architecture:** A Python package with a file-backed registry, deterministic keyword router, context packer, and CLI. The MVP avoids external dependencies so it works anywhere.

**Tech Stack:** Python 3.10+, Markdown skill files, JSON CLI output, pytest/unittest-compatible tests.

---

## Task 1: Create project skeleton

**Objective:** Establish a runnable Python package.

**Files:**
- Create: `pyproject.toml`
- Create: `src/skillhub/__init__.py`
- Create: `src/skillhub/cli.py`
- Create: `tests/test_router.py`

**Verification:** Run `python -m skillhub.cli --help` with `PYTHONPATH=src`.

## Task 2: Implement skill parsing

**Objective:** Load Markdown files into Skill objects with name, description, tags, and content.

**Files:**
- Create: `src/skillhub/registry.py`
- Test: `tests/test_registry.py`

**Verification:** Run `PYTHONPATH=src python -m unittest discover -s tests`.

## Task 3: Implement relevance routing

**Objective:** Suggest skills for a natural-language task and provide reasons.

**Files:**
- Create: `src/skillhub/router.py`
- Test: `tests/test_router.py`

**Verification:** Run unit tests and a CLI suggest command.

## Task 4: Implement context packing

**Objective:** Emit a compact skill context block in text or JSON.

**Files:**
- Create: `src/skillhub/packer.py`
- Test: `tests/test_packer.py`

**Verification:** Run `python -m skillhub.cli pack "debug pytest" --registry examples/skills`.

## Task 5: Implement maintenance checks

**Objective:** Flag skills that need metadata, examples, verification steps, or refresh.

**Files:**
- Create: `src/skillhub/maintenance.py`
- Test: `tests/test_maintenance.py`

**Verification:** Run `python -m skillhub.cli audit --registry examples/skills`.

## Task 6: Add docs and example skill

**Objective:** Make the project understandable and demoable.

**Files:**
- Create: `README.md`
- Create: `docs/vision.md`
- Create: `docs/architecture.md`
- Create: `examples/skills/python-debugging.md`

**Verification:** Run the quick-start commands from README.
