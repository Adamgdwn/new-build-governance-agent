## Security Policy

### Supported Versions

| Version | Supported |
|---------|-----------|
| 0.3.x   | Yes       |
| < 0.3   | No        |

### Reporting a Vulnerability

Do **not** open a public GitHub issue for security vulnerabilities.

Email **adamgoodwin@shaw.ca** with:
- A description of the vulnerability and the affected component
- Steps to reproduce or a minimal proof of concept
- Any suggested mitigations if you have them

Expected response: acknowledgement within 5 business days, resolution or status update within 30 days.

### Scope

In scope:
- Secrets leaking through subprocess output or log files
- Arbitrary command execution via unsanitised plan fields
- Privilege escalation through the promotion execute pipeline

Out of scope:
- Vulnerabilities in third-party tools invoked by checks (pytest, npm, etc.)
- Issues requiring physical access to the developer workstation
- Social engineering

### Secret Handling

- Never print or commit values from `.env.master` or any live credential file.
- Use `master-env-run` wrappers for provider-backed commands; do not expand secrets into shell arguments.
- `promotion_checks.py` redacts `KEY=VALUE` lines from subprocess output before storing in reports. If you find a bypass, report it as a vulnerability.
