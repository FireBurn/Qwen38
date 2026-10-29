# GDN reader indexing: CPU saving, no qualified token-rate gain

The reader-index candidate remains experimental. The fixed 24-process A/B test did **not** establish an incremental speedup over the same library's legacy path. The previously qualified Q3/cap400 build is unchanged. No faster mega kernel is claimed.

## Hypothesis and correctness

Nested host profiling found about 101 ms of GDN state-copy reader scanning per 128-requested-token generation. The original helper searches for a nearby copy, then scans remaining graph nodes and sources to reject other readers. The candidate builds a graph-local index of GDN-root readers and retains all original type, shape, copy, offset and alias checks. It does not cache across graphs or change Vulkan resource lifetimes, shaders or submission settings.

Modes are `GGML_VK_GDN_READER_INDEX=0` (legacy/default), `1` (index), `2` (index plus full legacy oracle). Five cases covered short generation, coding, maths, populated KV and a KV boundary transition. Both indexed modes matched all requested native target-logit bits and token/counter references. Verification performed **13,440 decisions with zero mismatches**. No new GPU errors were reported.

## Fixed under-load A/B

Twenty-four fresh 512-token processes formed six alternating ABBA/BAAB blocks at cap400, with the same Q3 shaders and uninstrumented candidate library. Only index mode changed. CPU work and compiles were allowed throughout. Preset matching used external CPU, build count and runnable load; natural GPU clocks were outcomes.

The raw all-block estimate was **+1.72%, descriptive 95% interval −1.44% to +4.98%**. Only three blocks met external-load matching, below the required four. Their effects were −1.23%, −0.31% and −1.14%. All outputs and counters matched, with no new GPU errors. The positive raw blocks coincided with load imbalances: this is evidence against treating the raw average as a gain, not a qualified regression estimate.

No samples were added to rescue this result. An unused independent-confirmation proposal was written 13 seconds after the analysis file completed, before inspection; it is not a preregistration for that completed dataset. Its positive-result trigger failed and the stage was not run.

## Why the CPU optimization did not qualify

A separate diagnostic used one warmup and eight resident 128-token generations, four per mode. Minimal nested CPU timers measured:

| Mean per generation | Legacy | Indexed |
|---|---:|---:|
| Whole graph CPU scope | 474.86 ms | 437.13 ms |
| Reader query CPU scope | 71.37 ms | 2.83 ms |
| Index construction CPU scope | 0 | 27.23 ms |

The graph scope includes index construction and destruction. These nested measurements include timer overhead; do not add them or infer GPU time. All nine generations matched native tokens/counters and had no new GPU errors. This supports a real host-work reduction, with a substantial construction cost. It does not establish a token-rate improvement. GPU work or CPU/GPU overlap hiding the saving is a hypothesis requiring GPU measurements.

The next diagnostic uses the existing backend GPU timestamp logger to rank operation families before selecting a GPU-side optimization. Its altered synchronization prevents a throughput claim. Further changes must beat the preserved qualified configuration, rather than an altered legacy control.

## Evidence

- [Candidate, plans, builders and analyses](../archive/isolated/native-gdn-reader-index/PLAN.md)
- [Fixed A/B report](../archive/isolated/native-gdn-reader-index/timing512/20261029T123413Z/confirmation-analysis.json)
- [CPU diagnostic plan](../archive/isolated/native-gdn-reader-index/COST-PLAN.md)
- [CPU diagnostic results](../archive/isolated/native-gdn-reader-index/cost-runs/20261029T125531Z/analysis.json)
- [Initial host profile](../archive/isolated/native-host-planning-profile/runs/20261029T122045Z/analysis.json)

## GPU diagnostic: matrix operations dominate this short context

Two bounded 32-requested-token runs used the unchanged frozen qualified library and its existing timestamp logger: isolated operations and concurrent dependency groups. Both produced all 34 expected tokens with no new GPU errors. Matrix-containing records represented 85.88% and 86.52% of recorded time; attention-containing records 0.89% and 0.84%; GDN-containing records 1.05% and 1.61%. The largest grouped record was the paired Q3 gate/up matrix-vector operations, at 14.94%, followed by Q4/Q5 down projections.

These shares include prompt processing and warm generation. Logger synchronization changes overlap and submission, and grouped records include all named members. They are diagnostic shares, not an uninstrumented critical-path decomposition or an upper bound on fusion gains. Short-context attention shares do not generalize to long KV. The result prioritizes matrix shaders and their adjacent fusion opportunities over more host reader caching or short-context FA alone. It does not prove a particular shader change will help.

[GPU diagnostic records and parsed rows](../archive/isolated/native-gdn-reader-index/gpu-profile-summary.json).
