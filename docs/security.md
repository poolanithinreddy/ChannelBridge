# Security review

JWT authentication, server-side RBAC, tenant-scoped routes, ORM parameterization, safe filenames, bounded uploads, hardened XML parsing, restrictive CORS, security headers, hashed passwords, one-time webhook secrets, and audit events cover the primary demo threats. Webhooks accept only internal Compose or localhost targets. Artwork URLs are never fetched. Uploaded feeds and tokens are not logged.

Limitations: local JWT secrets and demo credentials are intentionally public; there is no production key management, distributed rate limiter, malware scan, TLS termination, secret rotation, or formal compliance assessment. The service is an educational application, not a production security certification.

