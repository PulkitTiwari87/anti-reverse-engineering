# Contributing

Thanks for helping. This project is small on purpose: keep changes focused.

## Setup

```bash
python -m pip install -r requirements.txt
make check
```

`make check` runs unit tests, policy validation, the skill sync check, and Markdown
lint (lint needs Node.js; it runs `npx markdownlint-cli2`). Without `make`, see
[docs/testing.md](docs/testing.md).

## Editing the skill

`skills/anti-reverse-engineering/SKILL.md` is canonical. After editing, run:

```bash
python scripts/check_skill_sync.py --write
```

This refreshes `.agents/skills/anti-reverse-engineering/SKILL.md`. CI fails if they differ.

## Pull request requirements

- `make check` passes (or explain exactly which part could not run).
- New behavior has a test; tests need no network access.
- Docs updated when behavior or policy fields change; update
  [docs/configuration.md](docs/configuration.md) and the policy reference together.
- Use the four decision outcomes consistently. Do not add new names.
- No real credentials, customer data, or private application details in examples.
- Do not add claims of guaranteed protection or legal certainty.

## Scope

In scope: the skill, policy schema and validator, integrations for agents, docs, tests.
Out of scope: offensive anti-analysis, malware evasion, obfuscation tools, and anything
that implies the skill enforces access control by itself.

By contributing you agree your contribution is licensed under the project license, and
you agree to follow the [Code of Conduct](CODE_OF_CONDUCT.md).
