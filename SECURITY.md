# Security notes

The application is a single-user local demonstration. It binds loopback, restricts trusted Host values and CORS origins, validates Pydantic event/claim schemas and source references, uses parameterized SQLite queries, rejects remote inference URLs, caps request size and request frequency, serializes model runs, and applies model/whole-workflow timeouts. React renders untrusted strings as text; no HTML injection or eval is used. Outputs require exact source evidence and numeric recount before publication.

No paid credential is accepted by the inference adapter. The local SDK's placeholder key is `local-no-key`, not a secret. `.env`, virtual environments, runtime databases, downloaded models, logs and tooling caches are ignored and excluded from release archives. No credentials were supplied or committed. Common credential patterns are checked by scripts/security_audit.py.

Executed dependency scans are stored in docs/reports/pip-audit.json and npm-audit.json. These report no known vulnerabilities at scan time; they do not prove the absence of vulnerabilities. Vite was upgraded from 7.1.12 to patched 7.3.7 following the initial audit. The common-pattern source scan is not a full security assessment or comprehensive secret detector.

Limits: no authentication/multi-tenancy, no TLS terminator, no distributed rate limit or production observability, no adversarial load test. Do not expose the Python API publicly without appropriate authentication, request streaming/memory protections and deployment hardening. Static public replay contains only original synthetic data and recorded outputs. Untrusted model notes remain explicitly marked and are never treated as verified publication text.
