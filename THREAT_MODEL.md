# Threat model
Protected assets: fictional event integrity, analyst decisions, operator credentials/session tokens, exports, and training availability. Trust boundaries: browser/API validation, API/role dependencies, persistence/foreign keys, report escaping, and locally stored evidence versus independent custody.

Threats mitigated: unauthenticated API reads, viewer mutation/export, malformed or unexpected event fields, non-documentation targets, duplicate conflict replay, cross-origin browser writes, note XSS, CSV formulas, SQL injection, expired sessions, and accidental retention of unneeded records. Parameterized Core statements and escaped React/PDF rendering keep user text as data.

Residual threats: host/browser compromise, stolen active cookies, privileged database rewriting, unbounded historical source replay under adversarial volume, process-local rate counters, absence of a distributed coordination design, unknown dependency advisories, and deployment mistakes. Local fingerprints do not prove independent chain of custody. Browser mode is deliberately user-controlled and has no authentication guarantee.

Deployment review must add TLS/secrets management, representative validation, independent security review, approved retention/backup custody, least-privilege host access, monitored availability, and a reviewed multi-worker design if scaling beyond the validated single process. No operational infrastructure interfaces or executable containment actions exist.
