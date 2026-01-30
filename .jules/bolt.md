## 2024-05-24 - Parallel FFmpeg Execution
**Learning:** Sequential execution of independent FFmpeg commands is a major bottleneck. Parallelizing them using `ThreadPoolExecutor` yielded a ~3x speedup on a 4-core machine.
**Action:** When processing multiple media segments, always look for opportunities to parallelize subprocess calls. Limit per-process threads (e.g., `-threads 1`) to avoid CPU thrashing.
