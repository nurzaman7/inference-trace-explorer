# Contributing Guide

## Scope

This repository is an ML observability system prototype. Contributions should preserve:
- trace schema compatibility
- deterministic test behavior
- clear API contracts
- low-friction local run

## Local Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

## Development Workflow

1. Create feature branch.
2. Implement focused changes.
3. Add or update tests under `src/tests/`.
4. Run checks before PR:

```bash
python -m compileall src examples
pytest -q src/tests
```

## Code Standards

- Use type hints.
- Keep interfaces backward-compatible unless intentionally versioned.
- Keep request/response models in `src/api_models.py`.
- Add docs updates for new endpoints/features.

## PR Checklist

- [ ] Tests pass locally.
- [ ] README/docs updated.
- [ ] New endpoints documented.
- [ ] No secrets committed.
