# Matched A/B measurements under background load

**No speedup was confirmed.** At the user's request, a separate under-load experiment proceeded without the CPU/build quiet gate. It retained model-output checks, serial GPU use, exact library/driver selection, hardware telemetry and driver-error checks. The original quiet queues remain unchanged.

## Independent confirmation

An 18-run screen compared stock and all eight combinations, forward/reverse. Before that screen finished, a fixed confirmation protocol was recorded: always test all three changes together, plus the highest-scoring enabled screen candidate if different, against unmodified stock. Q3-only was selected. The screen was candidate selection, not confirmation.

Confirmation used 18 fresh process runs: six per setting, arranged in three symmetric blocks with rotated order. Each run requested 512 tokens; the first 17 generated tokens formed the warm window, leaving 496 tokens in the steady window. All 36 screen/confirmation runs generated the same 513 token IDs, with 279 drafted and 234 accepted.

| Setting | Mean steady tokens/s | Block-paired speed change vs stock | Descriptive 95% interval |
|---|---:|---:|---:|
| Unmodified stock | 38.453 | reference | — |
| All three changes | 38.480 | +0.07% | −1.79% to +1.96% |
| Q3 correction only | 38.418 | −0.09% | −1.79% to +1.64% |

The sign of each effect changed between blocks. Neither interval excludes zero, so these measurements do not confirm a gain. No quiet-performance or deployment claim follows.

[Fixed plan](../archive/isolated/production-native-fusion/under-load-confirmation-plan.json), [selected candidates/order](../archive/isolated/production-native-fusion/under-load-confirmation512/20261028T172500Z/protocol.json), [block analysis](../archive/isolated/production-native-fusion/under-load-confirmation512/20261028T172500Z/confirmation-analysis.json), [all confirmation runs](../archive/isolated/production-native-fusion/under-load-confirmation512/20261028T172500Z/results.json).

## Workload comparability and limits

Background work continued. Each block required mode-mean CPU load within five percentage points, GPU-clock means within 3%, and background-build counts within two processes. All three blocks met those predeclared limits. Individual runs still experienced different load and GPU clocks; balanced order reduces linear drift rather than making the environment identical.

Every run had sufficient active-clock samples and no steady sensor errors, monitor failures or new target-driver errors. Full per-arm telemetry is archived beside the result files. A supplementary process-CPU observer began partway through confirmation and indicates sustained desktop CPU work; its incomplete coverage was not used in the primary comparison. [Supplementary observations](../archive/isolated/production-native-fusion/under-load-confirmation512/20261028T172500Z/supplementary-background-summary.json).

Intervals use a Student-t calculation over three symmetric-block log-speed contrasts, with two degrees of freedom. They are descriptive: the sample is small and temporal correlation remains possible. There was no optional stopping or extension selected on the outcome.

## Why the initial averages were insufficient

The screen gave stock 39.003 tokens/s, all three 39.167 and Q3-only 39.277. However, its return stock run had 59.3% CPU load versus 50.9% initially. The private control with all optimizations disabled averaged 39.459, ahead of every enabled setting. Small apparent improvements over stock therefore could not be attributed to the shader changes. Independent confirmation reduced the estimates to essentially zero. [Screen results](../archive/isolated/production-native-fusion/under-load512/20261028T171725Z/results.json).

Reducing instructions and VGPRs did not increase the reported wave-capacity field, and the dominant matrix weight formats/traffic remain unchanged. That plausibly limits benefit, but it is an inference rather than a measured bandwidth profile. The combined-path overlap also prevents adding separate estimated gains. These results motivate targeted profiling and host-overhead checks rather than claiming that accumulating arithmetic tweaks produces a faster model.

[Checked summary](../archive/isolated/production-native-fusion/under-load-results-summary.json), [complete experiment notes](../archive/isolated/production-native-fusion/STATUS.md).

## Later quiet-window evidence

The older queued workflow subsequently obtained a valid isolated GPU-timestamp result for the original fusion: 1.398 → 0.810 microseconds at 17,408 values, and 1.549 → 0.932 microseconds at 34,816 values, about 40–42% lower component time. These absolute savings are only about 0.6 microseconds per call. Even dozens of calls per generated token put the simple arithmetic scale in tens of microseconds, versus tens of milliseconds per generated token. That is an illustration, not a full-model prediction; command scheduling and cache effects can differ.

The following full-model pair was rejected: its native arm ran with about 3% CPU load, while the next arm saw about 47% and unsettled GPU clocks. Their reported 50.0 versus 38.9 tokens/s are **not a valid A/B comparison**. No new target-driver error was recorded. Dependent quiet-workflow helpers then exited on their predecessor checks; they are no longer live waiters. The user-authorized under-load results above remain authoritative for that experiment. [Queue audit](../archive/isolated/q3-pad112/earlier-quiet-queue-audit.json), [qualified component result](../archive/isolated/native-swiglu-q8/nativeopt-timing/timing/20261028T185406Z/checks.json).
