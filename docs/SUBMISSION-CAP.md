# Submission-size profiling and confirmation

This follow-up profiles the qualified padded-Q3 host, then tests an existing Vulkan submission-size option. The frozen library and shaders remain unchanged. No faster mega-kernel claim follows from these native-backend tests.

## Post-fix diagnostic

A separate `host-profile-v2` build adds nested CPU/wall scopes to the qualified guard-v2 source and rebuilds all three host translation units. It measures Q3 selection/MMVQ, descriptor requests/writes, command recording, nonempty submissions, graph recording, node processing, synchronization and fence waits. Sampling through `perf record` was unavailable; system settings were unchanged.

Each profile uses one warmup plus eight alternating native-control/padded generations of 128 requested tokens. All nine generations match prior native tokens and draft/accept counts, with no new driver errors. Counters cover each whole generation, including prompt work. Timers and atomics are intrusive; nested scopes overlap, and their durations must not be added or interpreted as GPU execution time. These profiles establish no throughput gain.

The padded selector now averages about 0.29 microseconds of measured CPU time per call. The native-control path bypasses this helper, so its zero count is intentional. Across four padded generations, the baseline profile records 896 graphs, 631,640 dispatches and 20,104 nonempty submissions: **22.4375 submissions per graph**. A nonempty submission averages about 15.5 microseconds of CPU time. Fence waits also consume substantial CPU, including deliberate spinning; removing spin time would not by itself prove lower latency.

The existing `GGML_VK_MAX_NODES_PER_SUBMIT` defaults to 100. Raising it to 400 reduces the same diagnostic's nonempty submissions to 16,836, or **18.7902 per graph**, while graph, node and dispatch counts remain identical. Other FLOP-based submission limits remain active, so quadrupling the node cap does not quarter submissions. Recorded submission CPU time falls from 77.8 to 69.2 milliseconds per padded generation, but these are separate instrumented runs under different background load; this is explanatory evidence, not a timing qualification.

## Qualification and predeclared experiment

Only `GGML_VK_MAX_NODES_PER_SUBMIT` changes between timed modes. Both use the same frozen qualified backend, private copy2 driver, production .27/.7 core/common, model, greedy MTP-max1 policy, 4k context, q8 KV and single CPU threads. Shaders, arithmetic and dispatch geometry are unchanged. Submission boundaries can affect CPU/GPU overlap, so lower submission counts need not improve throughput.

Caps 100, 200 and 400 all pass the 32-token full-vocabulary target-logit audit against the native reference SHA `75055a49a5844ad14030f45cb76c11de20a44a6bb0e2db7c1c89a616137eb576`. The selected cap400 also matches coding and math 128-token target-logit reference hashes exactly. All generated tokens and draft/accept counts match, with no new driver errors. These are requested target-logit checks, not captures of every internal draft tensor or long-context qualification. Some copied runner labels retain historical fusion names; actual masks/environment use padded Q3 only, with zero GLU fusion or quantizer overrides.

A fixed six-process screen runs caps 100/200/400/400/200/100, requesting 512 tokens each. Its means are 41.2211, 43.0907 and 43.2262 steady tokens/s respectively. The predeclared highest-mean rule selects cap400. The screen establishes no gain; independent confirmation is required regardless of its sign.

Confirmation fixes 24 fresh 512-token processes in six alternating ABBA/BAAB blocks, cap400 versus cap100. Matching uses CPU mode means within 5 percentage points, clocks within 3%, build-count difference at most two, runnable-task spread within max(4,15% of mean), settled arm clocks and a stable mapped libc inode. At least four matched blocks are required; all six blocks and all arms are retained. There is no performance-based extension. CPU/build load is allowed, with no quiet gate.

The primary comparison is incremental against the frozen padded-Q3 configuration at cap100. It is not a fresh stock comparison, and percentages must not be added to the historical stock result. Limited sample sizes and temporal correlation constrain descriptive t intervals.

## Confirmation result

All 24 arms completed, producing identical 513-token outputs, 279 drafts and 234 accepts, with no new GPU driver errors. Cap400 was faster in all six blocks. The all-block descriptive estimate is **+5.6433% [ +3.9991%, +7.3134% ]**, with pooled means 40.5940 versus 42.8900 steady tokens/s. This is an **unqualified** contrast: **zero blocks pass the predeclared matching rules**, so the experiment does not support adoption under that protocol.

Five blocks fail the between-mode clock criterion; the remaining block fails within-arm clock settling. CPU mode means are close (about 51% utilization), counted build-process means are zero, and CPU/build/runqueue gates pass. Every arm has valid telemetry. Clock changes systematically accompany cap400, but this experiment does not identify their cause. The original matching rules and rejected result remain unchanged.

A scheduling change can affect GPU utilization and natural DVFS as part of its total configuration effect. Conditioning on equal clocks may therefore answer a different question from practical throughput at unchanged system settings. This is a **new hypothesis after observing this result**, not a reason to retroactively relax the original gates. A separate fixed comparison must predeclare external-load matching, leave clocks/power settings untouched, report clocks as outcomes, and include unmodified stock before claiming that whole-configuration improvement. Keep the existing frozen configuration as the qualified baseline meanwhile.

Evidence: [profile comparison](../archive/isolated/q3-pad112/submission-count-profile.json), [predeclared plan](../archive/isolated/q3-pad112/submission-cap-plan.json), [confirmation](../archive/isolated/q3-pad112/submission-cap-confirm512/20261029T075159Z/confirmation-analysis.json), [exclusion details](../archive/isolated/q3-pad112/submission-cap-confirm512/20261029T075159Z/exclusion-details.json).
