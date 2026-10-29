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


## Separate whole-configuration confirmation

The adaptive follow-up was predeclared and published before collecting its new data. It fixes 36 fresh 512-token processes in six symmetric rotated ABC-CBA blocks: unmodified stock/cap100, frozen Q3/cap100 and frozen Q3/cap400. It matches **external** CPU/build/runqueue load, requires stable mapped libc and correct binaries, and treats natural clocks/power/temperature as **outcomes**. No clock, power-limit, affinity, desktop or system-library setting was changed. It estimates the total configuration effect under natural DVFS, not equal-clock shader efficiency. The original rejected clock-matched comparison remains rejected.

All six blocks pass the new external-load rules, with no exclusions. All 36 arms produce identical **513 tokens, 279 drafts and 234 accepts**, valid mandatory telemetry, and zero new driver errors. The steady decoding results are:

| Configuration | Mean steady tokens/s | Mean sampled active power |
|---|---:|---:|
| Unmodified stock, node cap100 | 39.2955 | 135.0 W |
| Frozen Q3, node cap100 | 40.5221 | 134.8 W |
| Frozen Q3, node cap400 | 42.6185 | 151.4 W |

The primary whole-configuration contrast is **+8.4302% versus stock**, descriptive 95% t interval **[+7.1698%, +9.7054%]**. The secondary incremental contrast is **+5.1451% versus frozen Q3/cap100**, interval **[+3.8100%, +6.4974%]**. These are direct contrasts in this new test, not sums of historical percentages. Full-generation throughput, including the initial warm window, also favours cap400: **+8.2571% [+7.0396%, +9.4884%]** versus stock. Full-generation and process costs are descriptive secondary outcomes.

Clocks are higher and more variable with cap400. Memory-clock samples remain 1258 MHz in all three modes; mean sampled active temperatures are approximately 58.44/58.44/58.65 C. Optional sensors have zero errors in this trial. The sampled power increase is a material tradeoff; it is not an integrated energy measurement or proof of the causal mechanism. Less submission work, changed overlap and natural clock behavior have not been isolated from each other. Six paired blocks and the adaptive experiment history limit the interpretation of the descriptive intervals.

### Populated-KV correctness

A separate stock100/frozen100/frozen400 audit uses the same deterministic longer prefix, 4k context, prefill batch4096/ubatch512 and 64 requested output tokens. All modes match at every requested target-logit row and generate the same 65 tokens, 36 drafts and 29 accepts. The audit spans positions **2580–2644**, with **72 full-vocabulary rows** and SHA `36d4469aa2ba81bc3cf6566bb73ee4312ecfe4b9673b12206ef0c197924669a5`. Padded modes exercise the cache, and no new driver errors occur. This extends correctness coverage beyond the short timing prompt; it is not a long-context speed result or proof for every context/internal draft tensor.

The frozen Q3 library and shader bytes remain unchanged. A separate qualification record and guarded reproduction wrapper select cap400 after checking the confirmation and populated-KV proof hashes. The wrapper is a private single-run reproduction, not a production deployment or another A/B qualification. The original cap100 snapshot remains available. The guarded smoke completes with 34 expected output tokens and zero new driver errors.

From the original `megakernel-review` workspace, a longer single-run reproduction is:

```sh
Q3_QUALIFIED_TOKENS=512 python3 -u isolated/run_private_guarded_batch.py run_q3_submit400_qualified_once.py
```

The wrapper defaults to 32 requested tokens and verifies the frozen snapshot and qualification proof hashes. The archive publishes evidence/source, while the command uses the existing local model, binaries and private driver.

The remaining contribution question is **stock with cap400 alone**. This experiment has not measured that mode, so it does not show how much of the gain requires the extra 3 GiB Q3 cache under the new scheduling policy. Test that directly before concluding the padded cache is necessary or the combination is optimal. No faster mega/FA kernel is established.

Follow-up evidence: [predeclared protocol](../archive/isolated/q3-pad112/submission-system-effect-plan.json), [36-arm confirmation](../archive/isolated/q3-pad112/submission-system-effect512/20261029T080536Z/confirmation-analysis.json), [clock/power and cost outcomes](../archive/isolated/q3-pad112/submission-system-effect512/20261029T080536Z/outcomes-summary.json), [populated-KV audit](../archive/isolated/q3-pad112/submission-populated-kv64/comparison.json), [scoped configuration](../archive/isolated/q3-pad112/submission-qualified-20261029.json).
