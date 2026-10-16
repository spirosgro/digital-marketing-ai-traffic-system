# UTM governance

Campaign URLs use lowercase, hyphenated values. The minimum fields are `utm_id`,
`utm_source`, `utm_medium`, `utm_campaign`, and `utm_content`. Google documents these
parameters for identifying campaigns in traffic-acquisition reporting.

Example:

```text
https://example.invalid/pilot-readiness?utm_id=C03&utm_source=municipal-newsletter&utm_medium=email&utm_campaign=pilot-readiness&utm_content=procurement-checklist
```

## Rules

- Register campaign values before launch.
- Never place names, email addresses, job titles, or sensitive attributes in URL parameters.
- Do not use UTMs as a substitute for lawful consent or a privacy notice.
- Keep redirect and shortened-link ownership documented.
- Test cross-domain behaviour and tag gating before release.
- Preserve source values. Correct mapping in transformation logic rather than editing history.

Source: https://support.google.com/analytics/answer/10917952
