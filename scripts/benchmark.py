#!/usr/bin/env python3
import platform,statistics,time
from generate_feed import generate
from app.validation.engine import validate
for size in (100,1000,10000):
    trials=[]
    for _ in range(3):
        data=generate(size,10);start=time.perf_counter();issues=validate(data);trials.append(time.perf_counter()-start)
    med=statistics.median(trials);print(f"records={size} trials=3 median_ms={med*1000:.2f} records_per_second={size/med:.0f} issues={len(issues)} os={platform.system()}-{platform.machine()}")
