# Dispatch coalescing — 2026-10-25

**Reference correction:** the 213-record checks use a saved mega baseline, not a fresh native run. See `../mtp-tape-replay/REFERENCE-PROVENANCE.md`.

Private prototype; not adopted and no throughput gain established.

## Design

Opt-in GGML_VK_MEGA_COALESCE=2..4, selected only for graphs with exactly 64 GLU nodes whose second dimension is 1 or 2. Disabled with verification replay, performance logger, or serialized submissions. Parent unified shader including FA unchanged.

Virtual boundaries retain a global shader barrier and finalize fusers only for their original segment suffix. Previously prepared tape stays visible to existing pending-record checks. Twelve direct native memory command sites gain flush hooks; deferred UMA memset flushes before its branch. Almost-ready/final submissions remain real. Joins stop at 3000 pending records or configured segment factor. Factor4 is implemented but untested.

## Evidence so far

Host compile completed (build.log). At 16 physical groups, control and factor2 each matched all 213 native full-vocabulary logits/hidden records across Roman and C++ prompts, with identical generated tokens and draft acceptance. Final twelve graphs had no native compute fallback.

Cumulative timestamp reports confirm actual dispatch reduction: last report 16.2 to 13.6 segments per mixed graph stream on both prompts. These reports include prefill/draft/catchup and are not target-only counts or asynchronous throughput measurements.

Graduated 64/128/192 correctness batch completed successfully; each size passed all 213 records for factor2. The 192 control also passed. Exact original quiet waiter resumed. Throughput diagnostic launched with eight symmetric arms: native, original parent, changed-host control, factor2, reverse. Qualification gate passed. Timestamp instrumentation disabled in throughput test.

## Limits

No quiet performance result, no broad corpus/stochastic validation, no factor4 qualification, no installed changes. Native command context assertions are conservative; multi-device/UMA paths are not qualified by these discrete-GPU tests. The previous occupancy discovery variant remains rejected for performance; this prototype tests the parent shader first.

## First asynchronous throughput result

Eight arms completed with identical 129 tokens and 55/74 acceptance counters. **Performance comparison invalid:** CPU load and clocks changed sharply across arms; coalesced-repeat drift was 40.04%, original-parent drift 18.05%, native drift 9.86%. Do not interpret the means as a coalescing gain. See throughput/*/validity.json and per-arm telemetry. Focused 64-FFN microbenchmark launched separately through the guard.

## Focused microbenchmark

64 small independent FFNs sharing quantized weights: all raw intermediates matched native at 16 and 192 groups. Dispatch count fell 8 to 5. Separate-arm timing appeared 1.85% faster on GPU but control GPU drift was 15.13%, so no performance conclusion.

Short ABBA blocks within one process (2048 graphs per group count, no timestamp queries) passed all native intermediates. At 16 groups: wall mean -1.89%, all 16 ABBA quartets faster (-3.96% to -0.89%). At 192: mean -7.19%, median -9.50%, but quartet range -18.23% to +12.46%; unstable. These are synthetic shared-weight results, not full-model gains.

A private LD_PRELOAD profiler now alternates target graphs in ABBA order and synchronizes every graph to isolate stage wall time. This changes pipeline overlap and is diagnostic only. Qualification at 16 groups then model profiling at 192 is in profile-run.log; inspect completion before relying on results.

## Profiler implementation correction

LD_PRELOAD attempt completed numerically but the interceptor never emitted graph records; its assertion failed and guard resumed the exact original waiter. It is not profiling evidence. No GPU fault occurred. A direct backend profiler is building in profile-host (profile-build.log), using the same coalescing source plus explicit per-graph synchronization and ABBA target selection. Scripts now target profile-direct16/192 and require direct log records. Qualify at 16 before 192.

A loader --help probe unexpectedly re-executed repeatedly; the exact private probe PID 624840 was stopped with SIGKILL after SIGTERM did not terminate it. It did not execute GPU work. Avoid invoking the LLVM loader directly for further diagnostics.

## Direct model profile completed

Direct profiler passed all 213 native full-vocabulary/hidden records and token/acceptance comparisons at both 16 and 192 groups. Model target verification segments fall 20 to 12. Startup quartet (0/273 segments during pipeline/descriptor registration) is retained in raw records and excluded from steady-state pairs.

At 192 groups all 15 steady ABBA quartets across two prompts were slower with joining: Roman mean +1.238%, C++ +1.262%, approximately +0.53 to +0.55 ms per target graph. This is synchronized stage wall timing under uncontrolled compilation, not asynchronous throughput. At 16 groups Roman -1.327%, C++ +0.821%, inconclusive. Full results in profile-analysis.json. Joining in its current form is not a win.

The existing preparation copies the entire growing prefix out and back at boundaries. opt-profile-host now preserves its allocation and copies only the unprepared suffix through a reusable scratch vector, retaining identical segment-local fusion scope and barriers. Private build started (opt-profile-build.log, unifiedexec session 2380). GPU qualification NOT yet performed. Next scripts: run_mtp_dispatch_coalescing_opt_profile16.py then run_mtp_dispatch_coalescing_opt_profile192.py through guard. Analyze with analyze_profiles.py profile-opt.

## Optimized preparation result

The reusable suffix scratch implementation passed all 213 native records and token/acceptance comparisons at 16 and 192 groups. At 192, joining remained slower on average: Roman +1.419%, C++ +1.804%; C++ median quartet was -1.481% with a wide -5.576% to +13.913% range. This did not establish a model speedup or isolate prefix copying as the earlier regression cause. No coalescing variant adopted.

A separate replay-input audit of the historical native 4086-node graph found all 2147 dispatches identical across nine adjacent steady graph comparisons (ten graphs), including keys, workgroups, push constants, and buffer tuples. This motivates a current mega-tape observer, not unvalidated replay. See replay-input-audit.json. New observer source/build is isolated/mtp-tape-replay; no replay implementation yet.
