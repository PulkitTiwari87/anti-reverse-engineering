import copy
import importlib.util
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "scripts" / "validate_policy.py"
FIXTURES = ROOT / "tests" / "fixtures"
FAKE_SECRET = "FAKE-NOT-A-REAL-SECRET"

spec = importlib.util.spec_from_file_location("validate_policy", SCRIPT)
vp = importlib.util.module_from_spec(spec)
spec.loader.exec_module(vp)


def valid_data():
    return vp.load_policy(FIXTURES / "valid-policy.yml")


def run_cli(*paths, extra=()):
    return subprocess.run(
        [sys.executable, "-I", str(SCRIPT), *extra, *map(str, paths)],
        capture_output=True, text=True, timeout=60)


class ValidatePolicyTests(unittest.TestCase):
    def write_tmp(self, text):
        tmp = tempfile.NamedTemporaryFile("w", suffix=".yml", delete=False, encoding="utf-8")
        tmp.write(text)
        tmp.close()
        self.addCleanup(Path(tmp.name).unlink)
        return tmp.name

    def test_valid_fixture_passes(self):
        errors, _ = vp.validate(valid_data())
        self.assertEqual(errors, [])

    def test_shipped_policies_pass(self):
        paths = [ROOT / ".anti-reverse-engineering.yml",
                 *sorted((ROOT / "policies").glob("*.yml")),
                 ROOT / "examples" / "owned-application" / ".anti-reverse-engineering.yml"]
        for path in paths:
            with self.subTest(path=path.name):
                errors, _ = vp.validate(vp.load_policy(path))
                self.assertEqual(errors, [])

    def test_missing_required_fields_fail(self):
        data = valid_data()
        del data["authorization"]["reverse_engineering"]
        del data["review"]
        errors, _ = vp.validate(data)
        self.assertTrue(any("authorization.reverse_engineering" in e for e in errors))
        self.assertTrue(any(e.startswith("review:") for e in errors))

    def test_missing_version_fails(self):
        data = valid_data()
        del data["version"]
        errors, _ = vp.validate(data)
        self.assertIn("version: required field is missing", errors)

    def test_wrong_version_fails(self):
        for bad in (2, "1", True):
            data = valid_data()
            data["version"] = bad
            errors, _ = vp.validate(data)
            self.assertTrue(any(e.startswith("version:") for e in errors), bad)

    def test_invalid_enum_fails(self):
        data = valid_data()
        data["authorization"]["reverse_engineering"] = "allow_everything"
        data["identity"]["changes_require_approval"] = ["logo", "colors"]
        errors, _ = vp.validate(data)
        self.assertTrue(any("authorization.reverse_engineering: not an allowed value" in e for e in errors))
        self.assertTrue(any("changes_require_approval[1]" in e for e in errors))

    def test_wrong_types_fail(self):
        data = valid_data()
        data["identity"]["preserve_by_default"] = "yes"
        data["application"]["repositories"] = "single/repo"
        data["application"]["name"] = 7
        errors, _ = vp.validate(data)
        self.assertTrue(any("preserve_by_default: expected boolean" in e for e in errors))
        self.assertTrue(any("repositories: expected list" in e for e in errors))
        self.assertTrue(any("application.name: expected string" in e for e in errors))

    def test_unknown_fields_fail_without_naming_them(self):
        data = valid_data()
        data["application"][FAKE_SECRET] = "x"
        data[FAKE_SECRET + "-top"] = "x"
        errors, _ = vp.validate(data)
        self.assertEqual(sum("unknown field" in e for e in errors), 2)
        self.assertFalse(any(FAKE_SECRET in e for e in errors))

    def test_non_mapping_root_fails(self):
        errors, _ = vp.validate(["a", "b"])
        self.assertEqual(len(errors), 1)
        self.assertIn("expected mapping", errors[0])

    def test_secret_printing_must_stay_disabled(self):
        data = valid_data()
        data["data_handling"]["never_print_secrets"] = False
        errors, _ = vp.validate(data)
        self.assertTrue(any("never_print_secrets" in e for e in errors))

    def test_unsafe_paths_rejected(self):
        for bad in ("/etc/passwd", "../outside", "C:\\Users\\x", "a/../../b"):
            data = valid_data()
            data["application"]["protected_paths"] = [bad]
            errors, _ = vp.validate(data)
            self.assertTrue(any("relative path" in e for e in errors), bad)
        data = valid_data()
        data["audit"] = {"location": "../elsewhere"}
        errors, _ = vp.validate(data)
        self.assertTrue(any("audit.location" in e for e in errors))

    def test_placeholder_is_warning_not_error(self):
        data = valid_data()
        data["application"]["owner"] = "<OWNER>"
        errors, warnings = vp.validate(data)
        self.assertEqual(errors, [])
        self.assertTrue(any("application.owner" in w for w in warnings))

    def test_malformed_yaml_fails_cleanly(self):
        path = self.write_tmp(f"version: [1\napplication: {FAKE_SECRET}\n  bad: : :\n")
        with self.assertRaises(vp.PolicyError) as ctx:
            vp.load_policy(path)
        self.assertNotIn(FAKE_SECRET, str(ctx.exception))

    def test_duplicate_keys_rejected(self):
        path = self.write_tmp("version: 1\nversion: 1\n")
        with self.assertRaises(vp.PolicyError):
            vp.load_policy(path)

    def test_unsafe_yaml_tag_is_not_executed(self):
        path = self.write_tmp("version: !!python/object/apply:os.getcwd []\n")
        with self.assertRaises(vp.PolicyError):
            vp.load_policy(path)

    def test_oversized_and_missing_files_rejected(self):
        big = self.write_tmp("a: " + "x" * (vp.MAX_BYTES + 1))
        with self.assertRaises(vp.PolicyError):
            vp.load_policy(big)
        with self.assertRaises(vp.PolicyError):
            vp.load_policy(FIXTURES / "does-not-exist.yml")

    def test_directory_is_not_scanned(self):
        with self.assertRaises(vp.PolicyError):
            vp.load_policy(FIXTURES)

    def test_cli_valid_exits_zero(self):
        result = run_cli(FIXTURES / "valid-policy.yml")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("OK", result.stdout)

    def test_cli_invalid_exits_nonzero_and_hides_values(self):
        result = run_cli(FIXTURES / "invalid-policy.yml")
        self.assertEqual(result.returncode, 1)
        output = result.stdout + result.stderr
        self.assertIn("INVALID", output)
        self.assertIn("authorization.reverse_engineering", output)
        self.assertIn("review.record_decision_rationale", output)
        self.assertNotIn(FAKE_SECRET, output)

    def test_cli_malformed_exits_nonzero_and_hides_values(self):
        path = self.write_tmp(f"key: [{FAKE_SECRET}\n")
        result = run_cli(path)
        self.assertEqual(result.returncode, 1)
        self.assertNotIn(FAKE_SECRET, result.stdout + result.stderr)

    def test_cli_strict_turns_warnings_into_failures(self):
        path = ROOT / "policies" / "default.yml"
        self.assertEqual(run_cli(path).returncode, 0)
        self.assertEqual(run_cli(path, extra=["--strict"]).returncode, 1)

    def test_cli_requires_a_file_argument(self):
        self.assertEqual(run_cli().returncode, 2)


if __name__ == "__main__":
    unittest.main()
