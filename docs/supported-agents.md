# Supported agents

Behavior depends on the client and its version. This page was written from the
repository's own design and was not verified against live vendor documentation in the
build session; confirm against your client's current docs.

## Codex and compatible clients

- **File:** `.agents/skills/anti-reverse-engineering/SKILL.md` (project-local).
- **Format:** Markdown with YAML frontmatter containing `name` and `description`.
- **Discovery:** clients typically read skill metadata at start-up, so restart the client
  after installing. Discovery locations and invocation differ across clients and versions.
- **Source of truth:** `skills/anti-reverse-engineering/SKILL.md`. The Codex copy is
  generated with `python scripts/check_skill_sync.py --write`, and CI fails on drift.

## Claude Code

- **File:** `.claude/commands/anti-reverse-engineering.md` (project) or
  `~/.claude/commands/anti-reverse-engineering.md` (all projects).
- **Format:** Markdown with optional frontmatter (`description`, `argument-hint`), where
  `$ARGUMENTS` is replaced with text typed after the command.
- **Use:** `/anti-reverse-engineering <task>`.
- **Important:** do not assume Claude Code loads Codex `SKILL.md` files automatically.
  The command tells the agent to read the skill file from `skills/` or `.agents/skills/`
  in the project, so copy those files too. Newer Claude Code versions may also support
  their own skill mechanism; check your version's documentation before relying on it.

## Other agents

Any agent that can read Markdown instructions can use `SKILL.md` as a system or project
prompt. Compatibility is untested. Adapters for more agents are on the roadmap (planned).

## Differences at a glance

| | Codex-style | Claude Code |
| --- | --- | --- |
| Entry point | Skill discovery | Slash command |
| Install location | `.agents/skills/` | `.claude/commands/` plus skill files |
| Needs restart | Usually | Usually not (command files are read on use) |
| Enforcement | None from this project | None from this project |
