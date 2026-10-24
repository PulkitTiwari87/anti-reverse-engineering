# Security policy

## Reporting a vulnerability

Do not open a public issue for a security problem.

Use GitHub private vulnerability reporting: on the repository page choose
**Security** then **Report a vulnerability**. The maintainer must enable this feature
in the repository settings after publication. If it is not available, contact the
maintainers at **<SECURITY CONTACT - REPLACE BEFORE PUBLICATION>**.

Please include what you found, how to reproduce it, and the affected files. Do not
include real secrets or customer data.

## What counts

- A way to make `scripts/validate_policy.py` execute code, read files, or leak values.
- Policy fields or documentation that cause an agent to disclose secrets.
- Workflow configuration that grants unnecessary permissions.

## What does not

Because the skill is advisory, an agent that ignores it is a documented limitation, not
a vulnerability of this project. See [docs/limitations.md](docs/limitations.md).

## Response

This is a volunteer-maintained project. No response-time guarantee is made.
Only the latest release receives fixes.
