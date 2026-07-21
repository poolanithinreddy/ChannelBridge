# Analytics query catalog

| Business question | SQL approach | Interpretation / process improvement | Limitation |
|---|---|---|---|
| Which errors recur? | `GROUP BY issues.code ORDER BY count(*) DESC` | Prioritize clearer docs and preflight validation | Seeded frequency is illustrative |
| Who retries most? | Sum `submissions.retry_count` grouped by partner | Review recurring integration blockers | A retry does not imply partner fault |
| What is the validation rate? | Successful submissions divided by all submissions | Track aggregate feed health | Mix and feed size affect the rate |
| Which categories dominate? | Group issues by category | Focus office hours and rules | Correlation is not causal impact |

Runtime query definitions live in `backend/app/api.py`; tenant-facing queries are partner-scoped. Indexes cover partner/date, category, severity, code, status, hashes, and issue fingerprints.

