#!/usr/bin/env python3
"""Check (or refresh with --write) that the Codex skill copy matches the canonical skill.

Canonical:   skills/anti-reverse-engineering/            (SKILL.md and references/)
Distributed: .agents/skills/anti-reverse-engineering/

Every file under the canonical directory must exist, byte-identical after line-ending
normalization, in the distributed directory, and the distributed directory must contain
no extra files. Standard library only.
Exit codes: 0 in sync, 1 drift or missing file.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CANONICAL = ROOT / "skills" / "anti-reverse-engineering"
DISTRIBUTED = ROOT / ".agents" / "skills" / "anti-reverse-engineering"


def _read(path):
    return path.read_bytes().replace(b"\r\n", b"\n")


def _files(base):
    return {p.relative_to(base) for p in base.rglob("*") if p.is_file()} if base.is_dir() else set()


def problems():
    src, dst = _files(CANONICAL), _files(DISTRIBUTED)
    found = [f"missing in distributed copy: {p.as_posix()}" for p in sorted(src - dst)]
    found += [f"extra in distributed copy: {p.as_posix()}" for p in sorted(dst - src)]
    found += [f"differs: {p.as_posix()}" for p in sorted(src & dst)
              if _read(CANONICAL / p) != _read(DISTRIBUTED / p)]
    return found


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    if not (CANONICAL / "SKILL.md").is_file():
        print("error: canonical skill missing: skills/anti-reverse-engineering/SKILL.md", file=sys.stderr)
        return 1
    if "--write" in argv:
        for p in _files(DISTRIBUTED) - _files(CANONICAL):
            (DISTRIBUTED / p).unlink()
        for p in _files(CANONICAL):
            (DISTRIBUTED / p).parent.mkdir(parents=True, exist_ok=True)
            (DISTRIBUTED / p).write_bytes(_read(CANONICAL / p))
        print(f"wrote {DISTRIBUTED.relative_to(ROOT).as_posix()}/")
        return 0
    found = problems()
    for message in found:
        print(f"error: {message}", file=sys.stderr)
    if found:
        print("edit the canonical files, then run: python scripts/check_skill_sync.py --write",
              file=sys.stderr)
        return 1
    print("OK skill copies are identical")
    return 0


if __name__ == "__main__":
    sys.exit(main())
