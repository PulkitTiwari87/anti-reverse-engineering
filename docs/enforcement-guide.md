# Enforcement guide

**Instructions guide an agent that chooses to follow them. Controls make an action
impossible or visible regardless of what the agent decides.** This project ships
instructions and light detection. Everything on this page is enforcement you must set
up yourself.

| Layer | Guidance (this skill) | Enforcement (your platform) |
| --- | --- | --- |
| Agent decides what to do | Yes | No |
| Agent can read a file | Says "minimize" | Filesystem and repo permissions |
| Agent can push or merge | Says "ask first" | Branch protection, required review |
| Agent can leak a secret | Says "never print" | Secret scanning, egress controls |
| Client can see business logic | Says "keep server-side" | Architecture and server authorization |

## Repository permissions

Give agents the least privilege that works: read-only for audits, scoped tokens for
writes, no production credentials in analysis environments. Separate roles for
maintainers and automation.

## Branch protection and required review

Protect `main`; require pull requests and at least one human review. Add CODEOWNERS for
identity-bearing paths (logos, brand assets, `LICENSE`, policy file) so changes there
always get an owner's review. Treat changes to `.anti-reverse-engineering.yml` as
security-relevant.

## Secret management and scanning

Keep secrets in a secret manager or environment injection, never in source. Enable
platform secret scanning and push protection where available. A clean scan is a scan
result, not proof that no secrets exist. Rotate on suspected exposure.

## Server-side authorization

Anything delivered to a browser or app can be inspected. Keep high-value business rules
and secrets on the server and authorize every sensitive operation there. Obfuscation
raises effort; it does not make client code secret.

## Build artifact exposure

Review what you ship: production source maps, debug symbols, internal endpoints in
bundles, and embedded keys. Publish only what clients need.

## External data transfer controls

Decide which external AI services may receive source or customer data. Enforce with
network egress rules, approved tooling, and organizational policy, then mirror the
decision in `authorization.external_upload_of_proprietary_material`.

## CI validation

This repository's workflows validate the policy and skill copies. In your project, run
`scripts/validate_policy.py` in CI so a broken policy cannot merge silently, give
workflows `permissions: contents: read`, and avoid repository secrets in PR jobs.

## Monitoring and incident response

Alert on bulk reads, mass downloads, secret access, and edits to identity assets. If
exposure occurs: limit access, preserve logs, rotate credentials, and follow your
organization's incident process.
