# Security notes

The local application binds loopback. The hosted Render profile binds the platform-provided port with exact host validation and configured CORS origins. Public demonstration endpoints serve synthetic events and licensed public historical results; they are not authenticated private-data services. Do not upload personal or confidential match data to a public demo.

Pydantic validates events/claims; SQLite writes are transactional and parameterized; POST bodies are limited before parsing, including chunked requests; rate/concurrency/time limits apply; local inference URLs are loopback-only and local LLM calls are rejected entirely on Render. Untrusted strings are rendered as text. Claims need exact evidence/numeric recount before publication. Historical model estimates are labeled, kept separate from factual results and checked against their data hashes and evaluation rules.

The frontend reads only a public backend origin from VITE_API_URL. It does not guess a public visitor's localhost service. No paid inference credential is used. Runtime files, .env, local model downloads, virtual environments and dependency folders are excluded from release archives. The historical corpus has its own licenses, revision URLs, hashes and attribution. No footage or club logos are packaged.

Executed pip/npm audits and a common-pattern source scan are in docs/reports. No known advisories or matching credential patterns were found in those scans at their recorded execution time. These are scoped checks, not guarantees that every vulnerability or secret type is absent. The separate Render-profile clean environment and browser integration were tested locally; actual Linux/Render/Vercel deployment and the real Google trigger remain unverified.

Limits: no production authentication/multi-tenancy, distributed limits, real load test or operational monitoring; Render Free SQLite/files are ephemeral; health pings do not guarantee uptime. Use the app as a public demonstration of synthetic/authorized public data. The original provisional competition audit remains explicit about production-readiness limits.
