# Sample audit report

Synthetic example of the report format. The application and findings are fictional.

```text
Target: Lumen Notes (example-studio/lumen-notes), server/sync-engine/
Task: Fix intermittent duplicate writes in the sync retry loop
Policy/authorization basis: .anti-reverse-engineering.yml (version 1) in repository root;
  task requested by a maintainer in the repository; path is listed under protected_paths
Decision: ALLOW WITH GUARDRAILS
Evidence considered: Policy permits maintenance; no external transfer needed;
  no real-secret files opened
Scope and data accessed (high level): 3 source files under server/sync-engine/,
  1 test file; no environment files, no customer data
Controls applied: Targeted reads only; no excerpts of internals in this report;
  change limited to the retry module
Verification performed: Unit tests for the retry module (all passed); full suite not run
Findings and limitations: Root cause was a missing idempotency check. Logo, product name,
  and attribution untouched. Tests cover the fixed path only.
Approval or follow-up required: Human review of the diff before merge (policy:
  high_risk_changes_require_human_review)
```
