# Native fusion-plan reuse

CPU fusion-plan caching is now implemented and numerically qualified for the sampled workloads. It has **not established an incremental token-speed gain** over the preserved padded-Q3/cap400 configuration. No Vulkan command buffers are replayed, and no new shaders are used.

The cache stores native fusion decisions, including GDN copy elision, RMS modes and write masks. Hits require matching ordered nodes/use counts, tensor metadata, buffer identities and destruction epoch, and relevant device options. Misses use the original planner. Entries belong to the backend context and own CPU data only; native recording, barriers, descriptors, submissions and resource lifetimes remain in use. Unsupported UMA, instrumentation and custom GLU-plan configurations bypass reuse. These are workload-specific guards, not a general backend lifetime proof.

## Correctness and invalidation

The initial canonical-key shadow found 53 hits in 61 graphs, but constructing its key cost about 3.37 ms per target graph. A faster snapshot validator subsequently matched 772 canonical hits in 825 graphs, with zero false positives or plan differences across 1,013,177 matching decision records. Mean target validation CPU time was 347 microseconds, versus 5,509 microseconds for the full key plus snapshot in that instrumented run. This comparison is validation overhead, not a speedup versus native planning.

Actual reuse and an oracle mode that recomputes every native decision both passed five target-logit cases: short generation, coding, mathematics, populated KV, and a KV boundary. All **530 target rows** were bit-identical to the preserved reference, with matching tokens and acceptance counters. Each mode exercised 1,013,177 cached decision records. No new GPU errors were observed.

Additional CPU tests extracted the exact validator functions and used the real tensor layout with mocked graph/device/buffer APIs: 1,379 checks passed, including every tensor byte, graph identities/use counts, device and buffer changes, and protected-memory stale-pointer ordering witnesses. These mocks do not establish every Vulkan lifetime property.

A real GPU mutation test changed RMS output flags and epsilon while varying input values on the same tensors. All 16 generations per mode matched exactly across frozen, oracle and actual reuse, including requested intermediate materialization. No decision mismatches or new GPU faults occurred.

## Fixed full-model A/B under background load

The predeclared experiment ran 24 fresh 512-token processes in six alternating ABBA/BAAB blocks. Both arms used the same synchronized runner, driver, model, activation policy and cap400. The control was the preserved qualified configuration. Every generation matched 513 output tokens, 279 drafts and 234 accepts.

| Result | Observation |
|---|---:|
| All-block descriptive speed change | −6.77% |
| Descriptive t95 interval | −17.69% to +5.61% |
| Mean steady token rate, control / reuse | 33.89 / 31.66 |
| Blocks passing predeclared external-load matching | 1 of 6 |
| Incremental gain established | No |

Matching used CPU busy fraction, build count, runnable tasks and valid telemetry; natural clocks and power were recorded as outcomes. Only one matched block is insufficient for the planned primary estimate. The raw regression also gives no reason to adopt this cache. All six blocks remain reported; there is no conditional confirmation, extension or selective retry of this dataset.

## Separate resident CPU diagnostic

The fixed 24-arm resident diagnostic completed, with both inactive and active warmups and 26 exact generations overall. Both modes used the same instrumented private library. Two thread-CPU timer reads per graph measured host work; synchronization bounded wall time. Native cached decisions were actually used, with zero decision mismatches or new GPU faults.

Across all six retained blocks, graph thread CPU time fell **23.05%**, descriptive t95 interval **−30.89% to −14.32%**. Every block showed a CPU reduction; the two externally matched blocks showed −16.63% and −20.76%. Mean graph CPU per generation was 606.0 ms inactive versus 461.7 ms active. Active validation cost 60.1 ms and canonical miss construction 5.9 ms per generation on average, already included in the active total.

Full generation wall time changed **+0.40%**, descriptive interval **−5.91% to +7.14%**. Only two blocks met the predeclared external-load criteria, so neither matched primary interval qualifies. The CPU reduction is useful mechanism evidence, with background-load caveats; it establishes no token-speed gain. CPU/GPU overlap or a GPU bottleneck could hide host savings, but this diagnostic does not isolate the cause. The instrumented resident dataset is not pooled with, or a confirmation of, the failed fresh-process experiment.

Further planner tuning is lower priority until a timeline or critical-path measurement identifies exposed host stalls. Keep the preserved qualified configuration; no cache adoption or faster mega-kernel claim.

[Resident analysis](../archive/isolated/native-fusion-plan/cpu-diagnostic/20261029T201643Z/analysis.json), [behavior checks](../archive/isolated/native-fusion-plan/cpu-diagnostic/20261029T201643Z/behavior-check.json), [predeclared CPU diagnostic](../archive/isolated/native-fusion-plan/CPU-DIAGNOSTIC-PLAN.md).

Evidence: [validator summary](../archive/isolated/native-fusion-plan/validator-summary.json), [actual reuse](../archive/isolated/native-fusion-plan/reuse-summary.json), [CPU checks](../archive/isolated/native-fusion-plan/cpu-validator/checks.json), [GPU mutations](../archive/isolated/native-fusion-plan/mutation/checks.json), [full-model A/B](../archive/isolated/native-fusion-plan/model-timing512/20261029T195456Z/confirmation-analysis.json), [predeclared timing plan](../archive/isolated/native-fusion-plan/MODEL-TIMING-PLAN.md), [cache implementation patch](../archive/isolated/native-fusion-plan/reuse.patch).
