# Security controls

Recommend these; do not pretend the skill implements them. Detail and rollout advice:
`docs/enforcement-guide.md` in the distribution repository.

1. **Repository access:** least-privilege roles, protected branches, required review,
   audit logs, separate production permissions.
2. **Secrets:** secret manager or environment injection, none in source control, secret
   scanning, rotation when exposure is suspected.
3. **Architecture:** secrets and high-value business rules stay server-side; authorize
   every sensitive server operation.
4. **Build and deploy:** limit source maps and debug artifacts in production; protect CI
   credentials; sign releases where appropriate.
5. **Agent permissions:** read-only by default for audits, approval gates for writes,
   narrow tool scopes, untrusted analysis kept away from production credentials.
6. **Data egress:** decide which external services may receive source or customer data;
   redact and minimize before approved transfers.
7. **Monitoring:** alert on bulk reads, secret access, mass downloads, and changes to
   identity-bearing assets.
8. **Verification in CI:** tests, policy validation, secret and dependency scanning.
   Review results; tools miss things and raise false positives.
9. **Brand protection:** canonical asset locations, usage rules, CODEOWNERS on identity paths.
10. **Incident response:** limit access, preserve logs, rotate affected credentials,
    follow your organization's process.
