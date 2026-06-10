---
name: python-debugging
description: Debug Python failures systematically with tests, tracebacks, and minimal fixes.
tags: [python, debugging, tests, pytest]
---

# Python Debugging

Use this skill when the task involves Python errors, failing tests, tracebacks, or unexpected runtime behavior.

## Steps

1. Reproduce the failure with the smallest command possible.
2. Read the full traceback from the first relevant application frame.
3. Write or narrow a failing test before changing code.
4. Make one minimal fix.
5. Re-run the failing test.
6. Run the nearby test suite.

## Verification

A fix is not complete until the original failure command passes and at least one nearby regression test passes.

## Example

```bash
PYTHONPATH=src python -m unittest discover -s tests
```
