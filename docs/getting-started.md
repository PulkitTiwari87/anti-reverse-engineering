# Getting started

## 1. Get the files

```bash
git clone https://github.com/<OWNER>/anti-reverse-engineering.git   # replace <OWNER> after publication
```

Until the repository is published, copy the files from your local checkout.

## 2. Install into your project

For Codex-style clients:

```bash
mkdir -p your-project/.agents/skills
cp -r anti-reverse-engineering/.agents/skills/anti-reverse-engineering your-project/.agents/skills/
```

For Claude Code (project-local; use `~/.claude/commands/` instead for all projects):

```bash
mkdir -p your-project/.claude/commands your-project/skills
cp anti-reverse-engineering/.claude/commands/anti-reverse-engineering.md your-project/.claude/commands/
cp -r anti-reverse-engineering/skills/anti-reverse-engineering your-project/skills/
```

If you install the command globally, the project still needs the skill files at
`skills/anti-reverse-engineering/` (or `.agents/skills/...`) for the command to read.

## 3. Create a policy

```bash
cp anti-reverse-engineering/policies/default.yml your-project/.anti-reverse-engineering.yml
```

Edit it: replace every `<PLACEHOLDER>`, list your real identity assets, protected
paths, and sensitive-data paths. Pick a different profile from `policies/` if needed
([strict](../policies/strict.yml), [development-friendly](../policies/development-friendly.yml)).

## 4. Validate it

```bash
python -m pip install -r anti-reverse-engineering/requirements.txt
python anti-reverse-engineering/scripts/validate_policy.py your-project/.anti-reverse-engineering.yml
```

Warnings about placeholders are expected until you finish editing; add `--strict` to
make them fail.

## 5. First use

Ask your agent for a task and watch for an explicit decision line.

- Claude Code: `/anti-reverse-engineering fix the login redirect bug`
- Codex-style: mention the skill by name, or let the client discover it.

You should see one of `ALLOW`, `ALLOW WITH GUARDRAILS`, `PAUSE AND CLARIFY`, or
`REFUSE UNSAFE PORTION AND REDIRECT`. Try a few cases from
[examples/decision-cases.md](../examples/decision-cases.md) to confirm.

## 6. Add real controls

The skill is advisory. Set up repository permissions, branch protection, and secret
scanning as described in [enforcement-guide.md](enforcement-guide.md).
