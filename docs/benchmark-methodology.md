# Benchmark methodology

Run `make benchmark`. It generates deterministic 100, 1,000, and 10,000-record feeds, makes every tenth record invalid, performs three trials per size, and reports median validation time and records/second. Results depend on interpreter, CPU, memory pressure, and commit. No target is asserted in advance.

