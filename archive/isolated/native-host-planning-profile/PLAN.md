# Host planning cost profile

Clone qualified guard-v2; same shader objects, .27/.7 core and private copy2 driver. All three host TUs rebuilt. No observer trace collection, GPU commands added/skipped or numerical implementation change.

First fresh stock400/profile40032-token full-vocabulary target-logit audit, matching native75055... and all tokens/counters. Then one unmeasured warmup plus eight resident128-token control/padded generations at cap400, same greedyMTPmax1/4kctx/q8KV/1CPUthread. All nine generations must match prior native tokens/draft/accept counts; zero newdrivererrors and correct mappings. CPU/build load allowed,noquietgate,serialGPUguard.

Intrusive CPU/wall scopes: existing Q3/global recording/submit/graph/node/wait events, plus fusion selection, fusion alias checks, dependency checks, GDN state-copy search and empty-scope calibration. Nested metrics overlap; do not add. Clock/atomic overhead and instrumentation-induced cache/load changes prevent throughput inference or precise GPU-time attribution. Empty calibration is only an approximate timer-cost reference.

Source hypothesis: GDN state-copy verification scans remaining graph sources for each GDN, so repeated whole-tail reader checks may be avoidable with a per-graph reader index. Measure before implementing. A per-graph index would avoid cross-graph cache/lifetime issues while retaining the original alias/state-copy tests and GPU commands. No such index or speedup is established by this profile alone. Frozen qualified options remain unchanged.
