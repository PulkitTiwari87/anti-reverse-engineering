PYTHON ?= python
POLICIES = .anti-reverse-engineering.yml policies/default.yml policies/strict.yml policies/development-friendly.yml examples/owned-application/.anti-reverse-engineering.yml

.PHONY: test validate sync-check sync lint check

test:
	$(PYTHON) -m unittest discover -s tests -v

validate:
	$(PYTHON) scripts/validate_policy.py $(POLICIES)

sync-check:
	$(PYTHON) scripts/check_skill_sync.py

sync:
	$(PYTHON) scripts/check_skill_sync.py --write

# Requires Node.js; npx downloads markdownlint-cli2 on first use.
lint:
	npx --yes markdownlint-cli2@0.17.2

check: test validate sync-check lint
