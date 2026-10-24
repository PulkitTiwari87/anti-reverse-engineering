import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKIP_DIRS = {".git", "node_modules"}
BANNED_CLAIMS = re.compile(
    r"unhackable|military[- ]grade|clone[- ]proof|100%\s+(secure|protect|safe)|"
    r"cannot be (cloned|reverse[- ]engineered)\b|guarantees? (full |complete )?protection",
    re.IGNORECASE)
SECRET_PATTERNS = re.compile(
    r"AKIA[0-9A-Z]{16}|-----BEGIN [A-Z ]*PRIVATE KEY-----|\bsk-[A-Za-z0-9]{20,}|ghp_[A-Za-z0-9]{30,}")
LINK = re.compile(r"(?<!\!)\[[^\]]*\]\(([^)\s]+)\)|<img[^>]+src=\"([^\"]+)\"")


def markdown_files():
    return [p for p in ROOT.rglob("*.md") if not SKIP_DIRS & set(p.relative_to(ROOT).parts)]


def strip_fences(text):
    return re.sub(r"```.*?```", "", text, flags=re.DOTALL)


def slug(heading):
    heading = re.sub(r"[`*]", "", heading.strip().lower())
    return re.sub(r"\s", "-", re.sub(r"[^\w\s-]", "", heading))


class DocsTests(unittest.TestCase):
    def test_no_unsupported_protection_claims(self):
        for path in markdown_files():
            text = path.read_text(encoding="utf-8")
            with self.subTest(path=str(path.relative_to(ROOT))):
                self.assertIsNone(BANNED_CLAIMS.search(text))

    def test_limitations_are_stated(self):
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        self.assertIn("advisory", readme)
        self.assertIn("does not claim that reverse engineering or cloning can be", readme)
        limits = (ROOT / "docs" / "limitations.md").read_text(encoding="utf-8").lower()
        for phrase in ("advisory", "not proof of ownership", "public client-side"):
            self.assertIn(phrase, limits)

    def test_relative_links_resolve(self):
        for path in markdown_files():
            text = strip_fences(path.read_text(encoding="utf-8"))
            for match in LINK.finditer(text):
                target = match.group(1) or match.group(2)
                if re.match(r"^(https?:|mailto:|#)", target):
                    continue
                with self.subTest(path=str(path.relative_to(ROOT)), target=target):
                    file_part = target.split("#")[0]
                    self.assertTrue((path.parent / file_part).exists())

    def test_readme_anchors_match_headings(self):
        text = (ROOT / "README.md").read_text(encoding="utf-8")
        headings = {slug(m.group(1)) for m in re.finditer(r"^#{1,6}\s+(.+)$", strip_fences(text), re.M)}
        for anchor in re.findall(r"\]\(#([^)]+)\)", text):
            with self.subTest(anchor=anchor):
                self.assertIn(anchor, headings)

    def test_readme_lists_required_sections(self):
        text = (ROOT / "README.md").read_text(encoding="utf-8")
        for heading in ("Why this project exists", "Installation for Claude Code",
                        "Installation for Codex", "Threat model", "Known limitations",
                        "Roadmap", "FAQ", "License"):
            self.assertRegex(text, rf"(?m)^## {re.escape(heading)}$")

    def test_no_secret_like_strings_committed(self):
        for path in ROOT.rglob("*"):
            if not path.is_file() or SKIP_DIRS & set(path.relative_to(ROOT).parts):
                continue
            if path.suffix in {".md", ".yml", ".yaml", ".py", ".toml", ".svg", ".cff", ".jsonc", ".txt", ""}:
                with self.subTest(path=str(path.relative_to(ROOT))):
                    self.assertIsNone(SECRET_PATTERNS.search(path.read_text(encoding="utf-8", errors="ignore")))

    def test_makefile_targets_exist_for_documented_commands(self):
        makefile = (ROOT / "Makefile").read_text(encoding="utf-8")
        for target in ("test:", "validate:", "lint:", "check:", "sync-check:"):
            self.assertIn(target, makefile)


if __name__ == "__main__":
    unittest.main()
