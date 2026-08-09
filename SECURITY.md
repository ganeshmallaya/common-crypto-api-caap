# Security policy

CALI and the included service are exploratory research, not production-ready
cryptographic software. Do not expose the reference server to untrusted networks
or use it to protect production data or keys.

## Reporting a vulnerability

Use GitHub's **Report a vulnerability** flow in the repository Security tab so
the report remains private. Include:

- affected commit and file;
- reproducible steps or a minimal test case;
- expected and observed behavior;
- security impact and affected trust boundary; and
- any known workaround.

Do not open a public issue for an undisclosed vulnerability or include private
keys, credentials, customer data, exploit traffic, or other sensitive material.

The maintainer will acknowledge a valid private report when practical, assess
it against the research status, and coordinate disclosure if a correction is
published. No response-time, support, remediation, or security-assurance SLA is
offered.

## Supported versions

There is no supported production release. Only the current `main` research
state is considered for corrections; historical drafts and local backups are
not maintained releases.
