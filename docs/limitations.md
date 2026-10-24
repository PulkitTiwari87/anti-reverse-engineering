# Limitations

## What is not enforceable

- **The skill is advisory.** An agent can ignore it, and other agents may not load it.
- **It cannot restrict access an actor already has.** Anyone authorized to read code,
  assets, or behavior can copy what they can see.
- **It cannot enforce access control, block network traffic, protect secrets, or create
  audit logs** without separate tooling.
- **Public client-side code and observable behavior can be inspected.** Obfuscation raises
  effort; it does not make them secret.
- **A policy file is configuration, not proof of ownership** or legal authority, and it
  is not cryptographically enforced.
- **Scanners and checks** have false positives and false negatives. A clean result is not
  proof of absence.
- **Prompt injection is mitigated, not eliminated.** The skill tells agents to treat
  inspected content as data, but a model can still be misled.

## What it does not provide

- Legal advice or conclusions. Similarity of function or appearance does not by itself
  establish infringement; that needs qualified, jurisdiction-specific advice.
- DRM, copyright enforcement, or a guarantee of originality.
- Protection against a determined actor with full access.

## What is enforceable (by your platform, not by this project)

Repository permissions, branch protection, required review, secret scanning, egress
controls, server-side authorization, and monitoring. See
[enforcement-guide.md](enforcement-guide.md).

## What this project does check

Only file-level consistency: policy structure and values, identical skill copies, valid
Markdown, and that documentation avoids unsupported claims. See [testing.md](testing.md).

## Known gaps

- Agent compatibility beyond Codex-style discovery and one Claude Code command is untested.
- No behavioral test harness runs real agents; decision cases are manual.
- Workflows have not run on GitHub until the repository is published.
