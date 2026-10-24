# Policy reference

Canonical field list for `.anti-reverse-engineering.yml` (schema `version: 1`).
Full documentation with examples: `docs/configuration.md` in the distribution repository.
Machine check: `python scripts/validate_policy.py <file>`.

The policy is **configuration that describes intent**. It does not grant access, prove
ownership, or enforce anything. If it conflicts with the real tool permissions, the real
permissions win.

| Field | Type | Meaning for the agent |
| --- | --- | --- |
| `version` | integer, must be `1` | Schema version |
| `application.name` / `owner` | string | Who the protected application is and who controls it |
| `application.canonical_domains` / `repositories` | list of strings | Official locations; others are not assumed owned |
| `application.identity_assets` | list of paths | Brand assets: preserve, change only with approval |
| `application.protected_paths` | list of paths | Proprietary source: targeted reads only, never bulk export |
| `application.sensitive_data_paths` | list of paths | Secrets and customer data: never print values |
| `authorization.permitted_work` | list of enum | Work categories treated as in scope |
| `authorization.reverse_engineering` | enum | `deny`, `approval_required`, `allowed_in_documented_scope` |
| `authorization.third_party_reconstruction` | enum | `deny`, `deny_without_documented_authorization` |
| `authorization.external_upload_of_proprietary_material` | enum | `deny`, `approval_required`, `allowed_for_non_sensitive` |
| `identity.preserve_by_default` | boolean | Keep identity unless approved |
| `identity.changes_require_approval` | list of enum | Identity elements that need approval to change |
| `data_handling.*` | booleans | `never_print_secrets` must be `true` |
| `review.*` | booleans | Human review and rationale recording |
| `audit.report_format` / `audit.location` | enum / relative path | How decisions are reported and where notes live |

Interpretation rules:

- Missing optional field: use the most restrictive reasonable reading.
- `approval_required`: pause and ask before the action; an earlier approval does not carry over.
- A policy that loosens controls (`reverse_engineering: allowed_in_documented_scope`)
  still requires a documented scope in the task or repository.
