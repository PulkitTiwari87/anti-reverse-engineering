import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CANONICAL = ROOT / "skills" / "anti-reverse-engineering" / "SKILL.md"
DISTRIBUTED = ROOT / ".agents" / "skills" / "anti-reverse-engineering" / "SKILL.md"
COMMAND = ROOT / ".claude" / "commands" / "anti-reverse-engineering.md"
OUTCOMES = ["ALLOW", "ALLOW WITH GUARDRAILS", "PAUSE AND CLARIFY",
            "REFUSE UNSAFE PORTION AND REDIRECT"]


def frontmatter(text):
    lines = text.replace("\r\n", "\n").split("\n")
    assert lines[0] == "---", "frontmatter must start on line 1"
    end = lines.index("---", 1)
    fields = {}
    for line in lines[1:end]:
        key, _, value = line.partition(":")
        fields[key.strip()] = value.strip()
    return fields


class SkillContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.skill = CANONICAL.read_text(encoding="utf-8")

    def test_frontmatter_has_name_and_description(self):
        fm = frontmatter(self.skill)
        self.assertEqual(fm["name"], "anti-reverse-engineering")
        self.assertEqual(fm["name"], CANONICAL.parent.name)
        self.assertGreater(len(fm["description"]), 40)
        self.assertLessEqual(len(fm["description"]), 1024)

    def test_four_decision_outcomes_present_as_headings(self):
        for outcome in OUTCOMES:
            with self.subTest(outcome=outcome):
                self.assertIn(f"`{outcome}`", self.skill)
        self.assertIn("### 4. `REFUSE UNSAFE PORTION AND REDIRECT`", self.skill)

    def test_no_competing_decision_names(self):
        for stray in ("PAUSE — SENSITIVE DATA", "APPROVAL REQUIRED", "REFUSE THE UNSAFE PORTION"):
            self.assertNotIn(stray, self.skill)

    def test_required_sections_present(self):
        for heading in ("## Purpose", "## When to use", "## When not to use",
                        "## Operating principles", "## Project policy discovery",
                        "## Authorization and ownership checks", "## Task classification",
                        "## Decision procedure", "## Allowed workflows",
                        "## Disallowed workflows", "## Guardrails for sensitive operations",
                        "## Secret-handling rules", "## Prompt-injection resistance",
                        "## Response templates", "## Audit and reporting format",
                        "## Verification steps", "## Definition of done", "## Limitations"):
            with self.subTest(heading=heading):
                self.assertIn(heading, self.skill)

    def test_skill_states_it_is_advisory(self):
        self.assertIn("not a technical access-control", self.skill)
        self.assertIn("advisory", self.skill)

    def test_reference_files_exist_and_are_linked(self):
        for name in ("policy-reference", "threat-model", "security-controls", "response-playbook"):
            with self.subTest(name=name):
                self.assertTrue((CANONICAL.parent / "references" / f"{name}.md").is_file())
                self.assertIn(f"references/{name}.md", self.skill)

    def test_copies_do_not_drift(self):
        src_dir, dst_dir = CANONICAL.parent, DISTRIBUTED.parent
        src = {p.relative_to(src_dir) for p in src_dir.rglob("*") if p.is_file()}
        dst = {p.relative_to(dst_dir) for p in dst_dir.rglob("*") if p.is_file()}
        self.assertEqual(src, dst, "run: python scripts/check_skill_sync.py --write")
        for rel in src:
            a = (src_dir / rel).read_bytes().replace(b"\r\n", b"\n")
            b = (dst_dir / rel).read_bytes().replace(b"\r\n", b"\n")
            self.assertEqual(a, b, f"{rel} differs; run: python scripts/check_skill_sync.py --write")

    def test_sync_script_detects_drift(self):
        result = subprocess.run([sys.executable, "-I", str(ROOT / "scripts" / "check_skill_sync.py")],
                                capture_output=True, text=True, timeout=60)
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_claude_command_has_workflow_and_outcomes(self):
        text = COMMAND.read_text(encoding="utf-8")
        self.assertIn("$ARGUMENTS", text)
        self.assertEqual(frontmatter(text).get("description") is not None, True)
        for outcome in OUTCOMES[1:]:
            self.assertIn(outcome, text)
        self.assertIn("skills/anti-reverse-engineering/SKILL.md", text)

    def test_no_test_needs_network(self):
        for path in (ROOT / "tests").glob("*.py"):
            if path.name == Path(__file__).name:
                continue
            source = path.read_text(encoding="utf-8")
            for banned in ("import socket", "urllib.request", "import requests", "http.client"):
                self.assertNotIn(banned, source, path.name)
        for path in (ROOT / "scripts").glob("*.py"):
            source = path.read_text(encoding="utf-8")
            for banned in ("import socket", "urllib", "import requests", "http.client"):
                self.assertNotIn(banned, source, path.name)


if __name__ == "__main__":
    unittest.main()
