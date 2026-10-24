# Testing

Prerequisites: Python 3.9+ and PyYAML (`python -m pip install -r requirements.txt`).
Markdown lint also needs Node.js (it downloads `markdownlint-cli2` through `npx`).

## All checks

```bash
make check
```

Runs, in order: `test`, `validate`, `sync-check`, `lint`. Without `make`, run the
commands below individually. On Windows, `make` may need to be installed separately.

## Individually

| Command | Expected result |
| --- | --- |
| `python -m unittest discover -s tests -v` | All tests `ok`, exit code 0 |
| `python scripts/validate_policy.py .anti-reverse-engineering.yml policies/*.yml` | `OK <file>` per file; placeholder warnings are normal |
| `python scripts/check_skill_sync.py` | `OK skill copies are identical` |
| `npx --yes markdownlint-cli2@0.17.2` | No errors |

`policies/*.yml` is expanded by your shell; on shells without globbing, list the files
as the Makefile does.

## What the tests cover

- `test_validate_policy.py`: valid and invalid policies, missing fields, wrong types,
  bad enums, malformed or unsafe YAML, path rules, CLI exit codes, and that error output
  never contains values from the file.
- `test_skill_contract.py`: frontmatter, the four decision outcomes, required sections,
  reference files, no drift between skill copies, no network use in tests or scripts.
- `test_docs.py`: no unsupported protection claims, limitations stated, relative links
  and README anchors resolve, no secret-like strings, Makefile targets exist.

No test needs network access. Passing tests show the files are consistent; they do not
prove an agent will follow the skill. To test agent behavior, run the cases in
[examples/decision-cases.md](../examples/decision-cases.md) by hand against your client.
