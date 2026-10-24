#!/usr/bin/env python3
"""Validate .anti-reverse-engineering.yml policy files (schema version 1).

Checks structure, types, and enumerated values only. It does NOT verify ownership,
authorization, or legal status, and a valid file enforces nothing by itself.

Safety properties:
- Reads only the files named on the command line. No directory scanning, no network.
- Parses with yaml.safe_load semantics (no arbitrary object construction).
- Never echoes values from the file. Errors name the field path and the expected
  type or allowed values, never the offending value or the YAML source line.

Requires PyYAML (pip install -r requirements.txt).
Exit codes: 0 all valid, 1 invalid input, 2 usage error or missing dependency.
"""
import argparse
import re
import sys
from pathlib import Path

try:
    import yaml
except ImportError:  # reported in main()
    yaml = None

MAX_BYTES = 256 * 1024

PERMITTED_WORK = {
    "maintenance", "feature_development", "accessibility", "performance",
    "testing", "documentation", "security_testing", "interoperability", "migration",
}
IDENTITY_CHANGES = {
    "product_name", "logo", "brand_assets", "distinctive_user_flows", "attribution",
}

# kind: str | bool | str_list | enum | enum_list | relpath
SCHEMA = {
    "application": {
        "name": ("str", True),
        "owner": ("str", True),
        "canonical_domains": ("str_list", True),
        "repositories": ("str_list", True),
        "identity_assets": ("str_list", True),
        "protected_paths": ("str_list", True),
        "sensitive_data_paths": ("str_list", True),
    },
    "authorization": {
        "permitted_work": (("enum_list", PERMITTED_WORK), True),
        "reverse_engineering": (
            ("enum", {"deny", "approval_required", "allowed_in_documented_scope"}), True),
        "third_party_reconstruction": (
            ("enum", {"deny", "deny_without_documented_authorization"}), True),
        "external_upload_of_proprietary_material": (
            ("enum", {"deny", "approval_required", "allowed_for_non_sensitive"}), True),
    },
    "identity": {
        "preserve_by_default": ("bool", True),
        "changes_require_approval": (("enum_list", IDENTITY_CHANGES), True),
    },
    "data_handling": {
        "never_print_secrets": ("bool", True),
        "minimize_customer_data": ("bool", True),
        "external_services_require_approval": ("bool", True),
    },
    "review": {
        "high_risk_changes_require_human_review": ("bool", True),
        "record_decision_rationale": ("bool", True),
    },
    "audit": {
        "report_format": (("enum", {"none", "summary", "detailed"}), False),
        "location": ("relpath", False),
    },
}
REQUIRED_SECTIONS = {"application", "authorization", "identity", "data_handling", "review"}
PLACEHOLDER = re.compile(r"<[^<>\n]+>")


class PolicyError(Exception):
    """Raised for files that cannot be loaded. The message never contains file content."""


class _UniqueKeyLoader(yaml.SafeLoader if yaml else object):
    """SafeLoader that rejects duplicate mapping keys."""


def _construct_mapping(loader, node, deep=False):
    seen = set()
    for key_node, _ in node.value:
        key = loader.construct_object(key_node, deep=deep)
        if key in seen:
            raise yaml.constructor.ConstructorError(None, None, "duplicate key", key_node.start_mark)
        seen.add(key)
    return yaml.SafeLoader.construct_mapping(loader, node, deep)


if yaml:
    _UniqueKeyLoader.add_constructor(
        yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, _construct_mapping)


def load_policy(path):
    """Load a policy file into Python data, or raise PolicyError."""
    p = Path(path)
    if not p.is_file():
        raise PolicyError("not a readable file")
    try:
        if p.stat().st_size > MAX_BYTES:
            raise PolicyError(f"file larger than {MAX_BYTES} bytes")
        text = p.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        raise PolicyError("file is not valid UTF-8") from None
    except OSError:
        raise PolicyError("file could not be read") from None
    try:
        return yaml.load(text, Loader=_UniqueKeyLoader)  # noqa: S506 - SafeLoader subclass
    except yaml.YAMLError as exc:
        mark = getattr(exc, "problem_mark", None) or getattr(exc, "context_mark", None)
        where = f" near line {mark.line + 1}, column {mark.column + 1}" if mark else ""
        raise PolicyError(f"malformed YAML{where} (source text not shown)") from None


def _type_name(value):
    return type(value).__name__


def _unsafe_path(value):
    parts = value.replace("\\", "/").split("/")
    return value.startswith(("/", "\\")) or re.match(r"^[A-Za-z]:", value) or ".." in parts


def _check_value(path, value, spec, errors, warnings):
    kind = spec[0] if isinstance(spec, tuple) else spec
    allowed = spec[1] if isinstance(spec, tuple) else None
    if kind == "bool":
        if not isinstance(value, bool):
            errors.append(f"{path}: expected boolean, got {_type_name(value)}")
    elif kind == "str":
        _check_str(path, value, errors, warnings)
    elif kind == "relpath":
        if _check_str(path, value, errors, warnings) and _unsafe_path(value):
            errors.append(f"{path}: must be a relative path inside the repository")
    elif kind == "enum":
        if not isinstance(value, str) or value not in allowed:
            errors.append(f"{path}: not an allowed value; allowed: {', '.join(sorted(allowed))}")
    elif kind in ("str_list", "enum_list"):
        if not isinstance(value, list):
            errors.append(f"{path}: expected list, got {_type_name(value)}")
            return
        for i, item in enumerate(value):
            item_path = f"{path}[{i}]"
            if kind == "enum_list":
                if not isinstance(item, str) or item not in allowed:
                    errors.append(f"{item_path}: not an allowed value; allowed: {', '.join(sorted(allowed))}")
            elif _check_str(item_path, item, errors, warnings) and path.endswith(
                    ("_assets", "_paths")) and _unsafe_path(item):
                errors.append(f"{item_path}: must be a relative path inside the repository")
        if kind == "enum_list" and len(set(map(str, value))) != len(value):
            errors.append(f"{path}: contains duplicate entries")


def _check_str(path, value, errors, warnings):
    if not isinstance(value, str):
        errors.append(f"{path}: expected string, got {_type_name(value)}")
        return False
    if not value.strip():
        errors.append(f"{path}: must not be empty")
        return False
    if PLACEHOLDER.search(value):
        warnings.append(f"{path}: placeholder value still present; replace before relying on this policy")
    return True


def validate(data):
    """Return (errors, warnings) for already-parsed policy data."""
    errors, warnings = [], []
    if not isinstance(data, dict):
        return [f"<root>: expected mapping, got {_type_name(data)}"], warnings
    allowed_top = {"version"} | set(SCHEMA)
    if len(set(data) - allowed_top):
        errors.append(
            f"<root>: {len(set(data) - allowed_top)} unknown field(s) (names not shown); "
            f"allowed: {', '.join(sorted(allowed_top))}")
    if "version" not in data:
        errors.append("version: required field is missing")
    elif data["version"] is not True and data["version"] != 1 or isinstance(data["version"], bool):
        errors.append("version: must be the integer 1")
    for section, fields in SCHEMA.items():
        if section not in data:
            if section in REQUIRED_SECTIONS:
                errors.append(f"{section}: required section is missing")
            continue
        body = data[section]
        if not isinstance(body, dict):
            errors.append(f"{section}: expected mapping, got {_type_name(body)}")
            continue
        unknown = set(body) - set(fields)
        if unknown:
            errors.append(
                f"{section}: {len(unknown)} unknown field(s) (names not shown); "
                f"allowed: {', '.join(sorted(fields))}")
        for name, (spec, required) in fields.items():
            path = f"{section}.{name}"
            if name not in body:
                if required:
                    errors.append(f"{path}: required field is missing")
                continue
            _check_value(path, body[name], spec, errors, warnings)
    if data.get("data_handling", {}).get("never_print_secrets") is False:
        errors.append("data_handling.never_print_secrets: must be true; this tool rejects policies that allow printing secrets")
    return errors, warnings


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("files", nargs="+", help="policy files to validate (no directory scanning)")
    parser.add_argument("--strict", action="store_true", help="treat warnings (e.g. placeholders) as errors")
    args = parser.parse_args(argv)
    if yaml is None:
        print("PyYAML is required. Install it with: python -m pip install -r requirements.txt",
              file=sys.stderr)
        return 2
    failed = False
    for name in args.files:
        try:
            errors, warnings = validate(load_policy(name))
        except PolicyError as exc:
            errors, warnings = [f"<file>: {exc}"], []
        if args.strict:
            errors, warnings = errors + warnings, []
        status = "INVALID" if errors else "OK"
        print(f"{status} {name}")
        for message in errors:
            print(f"  error: {message}")
        for message in warnings:
            print(f"  warning: {message}")
        failed = failed or bool(errors)
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
