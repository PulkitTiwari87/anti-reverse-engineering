# FAQ

## Does this prevent all reverse engineering?

No. It helps cooperating agents avoid unauthorized reconstruction and unnecessary
exposure. Anyone with access to your shipped code, assets, or behavior can study it.

## Can it protect public frontend JavaScript?

Not by itself. Code and assets delivered to browsers can be inspected. Keep secrets and
high-value logic on the server. See [enforcement-guide.md](enforcement-guide.md).

## Does it block all reverse-engineering work?

No, and it should not. Authorized interoperability, migration, and defensive research are
allowed, with guardrails. It refuses only the unauthorized part, such as reconstructing a
protected third-party app or removing attribution.

## Can I use it on a competitor's product?

It is for protecting applications you control. Pointing an agent at someone else's
product does not make that work authorized, and the skill will refuse unauthorized
reconstruction. For legal questions, consult a qualified professional.

## Does a policy file prove ownership?

No. It is configuration describing intent. It does not prove ownership, grant access, or
enforce anything. Agents are told to treat it as data.

## Can I use it with other AI coding agents?

Possibly. Any agent that can read Markdown instructions can use `SKILL.md`. Only Codex-style
discovery and a Claude Code command are provided; others are untested. See
[supported-agents.md](supported-agents.md).

## What happens if an agent ignores the skill?

Nothing from this project: it is advisory. That is why repository permissions, branch
protection, secret scanning, and server-side authorization matter.

## Does it provide legal protection?

No. It is not legal advice and creates no legal rights.

## Why is it called anti-reverse-engineering?

The name describes the defensive objective: reducing unauthorized reconstruction. It is
not a claim that reverse engineering can be prevented.
