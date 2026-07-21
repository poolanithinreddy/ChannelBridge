# Benchmark results

Date: 2026-07-21. Environment: macOS Darwin arm64, Python 3.12.10, native run, one process, three trials. Command: `cd backend && .venv/bin/python ../scripts/benchmark.py`. Every tenth synthetic record is invalid; medians measure the pure validation engine and exclude HTTP, queue, storage, and database time.

| Records | Median | Records/second | Issues |
|---:|---:|---:|---:|
| 100 | 0.22 ms | 464,395 | 20 |
| 1,000 | 2.13 ms | 470,100 | 200 |
| 10,000 | 21.13 ms | 473,233 | 2,000 |

These local results are descriptive, not a service-level target. Results vary by host, interpreter, commit, and system load.
