# Configuration

The policy file is `.anti-reverse-engineering.yml` in the repository root, schema
`version: 1`. It describes intent for agents. It does not enforce permissions, and it is
not proof of ownership. Check any file with
`python scripts/validate_policy.py <file>`.

Unknown fields are rejected, so typos fail loudly. You can keep private details out of a
public repository by using generic path patterns, or by keeping the detailed policy in a
private repository or local file.

## Top level

| Field | Type | Required | Notes |
| --- | --- | --- | --- |
| `version` | integer | yes | Must be `1` |
| `application` | mapping | yes | |
| `authorization` | mapping | yes | |
| `identity` | mapping | yes | |
| `data_handling` | mapping | yes | |
| `review` | mapping | yes | |
| `audit` | mapping | no | |

## `application`

| Field | Type | Required | Meaning |
| --- | --- | --- | --- |
| `name` | non-empty string | yes | Application name |
| `owner` | non-empty string | yes | Owning person or organization |
| `canonical_domains` | list of strings | yes (may be empty) | Official domains |
| `repositories` | list of strings | yes (may be empty) | Official repositories |
| `identity_assets` | list of relative paths | yes (may be empty) | Brand assets to preserve |
| `protected_paths` | list of relative paths | yes (may be empty) | Proprietary source: targeted reads only |
| `sensitive_data_paths` | list of relative paths | yes (may be empty) | Secrets and customer data |

Paths must be relative to the repository. Absolute paths, drive letters, and `..` are
rejected. Glob-like patterns such as `.env*` are allowed and are interpreted by the agent.

## `authorization`

| Field | Allowed values |
| --- | --- |
| `permitted_work` (list) | `maintenance`, `feature_development`, `accessibility`, `performance`, `testing`, `documentation`, `security_testing`, `interoperability`, `migration` |
| `reverse_engineering` | `deny`, `approval_required`, `allowed_in_documented_scope` |
| `third_party_reconstruction` | `deny`, `deny_without_documented_authorization` |
| `external_upload_of_proprietary_material` | `deny`, `approval_required`, `allowed_for_non_sensitive` |

All four are required. `allowed_in_documented_scope` still requires a documented scope
for the specific task. There is deliberately no value that allows third-party
reconstruction without documented authorization.

## `identity`

| Field | Type | Meaning |
| --- | --- | --- |
| `preserve_by_default` | boolean | Keep identity unless approved |
| `changes_require_approval` | list of `product_name`, `logo`, `brand_assets`, `distinctive_user_flows`, `attribution` | Items needing approval to change |

## `data_handling`

| Field | Type | Notes |
| --- | --- | --- |
| `never_print_secrets` | boolean | Must be `true`; the validator rejects `false` |
| `minimize_customer_data` | boolean | |
| `external_services_require_approval` | boolean | |

## `review`

| Field | Type |
| --- | --- |
| `high_risk_changes_require_human_review` | boolean |
| `record_decision_rationale` | boolean |

## `audit` (optional)

| Field | Allowed values | Default behavior |
| --- | --- | --- |
| `report_format` | `none`, `summary`, `detailed` | Agent reports in chat only |
| `location` | relative path | No files written unless an authorized project practice exists |

## Profiles

| Profile | File | Use for |
| --- | --- | --- |
| Default | [policies/default.yml](../policies/default.yml) | Balanced everyday development |
| Strict | [policies/strict.yml](../policies/strict.yml) | Sensitive or regulated apps |
| Development-friendly | [policies/development-friendly.yml](../policies/development-friendly.yml) | Repositories you clearly own |

Even the development-friendly profile keeps secrets hidden and third-party
reconstruction gated. Worked example:
[examples/owned-application](../examples/owned-application/.anti-reverse-engineering.yml).
Short field reference used by the skill:
[policy-reference.md](../skills/anti-reverse-engineering/references/policy-reference.md).
