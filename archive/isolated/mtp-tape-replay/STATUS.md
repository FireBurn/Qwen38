# Tape replay status — 2026-10-25

**Reference correction:** the 213-record checks use a saved mega baseline, not a fresh native run. See `../mtp-tape-replay/REFERENCE-PROVENANCE.md`.

Observer complete; replay not implemented, no performance gain established.

## Verified

- Private capture backend compiled successfully.
- Guarded observer checks completed at 16 then 192 physical groups; exact original quiet waiter resumed. Session 47997 terminal0.
- Each group count matched all 213 native full-vocabulary logits/hidden records across Roman and C++ prompts, with identical tokens/acceptance and no native compute operations in final twelve graphs.
- 37 Roman + 32 C++ steady graphs at each bound: 138 observed total. Each contained 20 segments and 3440 records, all compiled tape bytes identical within its run. The entire 2048-slot descriptor range table was also identical within each run.
- Every steady graph issued one native memory operation. Replay cannot omit this. Source points to the ADD_RMS partial-sum preamble clear, but exact callsite/stage identification remains to be instrumented.
- Capture files add substantial CPU file I/O, so these runs are correctness/invariance evidence only.

See capture-analysis.json and raw capture16/192 artifacts. No invariant beyond these prompts, context region and process lifetime has been established.

## Next

Audit and identify the single native operation and any CPU deferred transfers. Keep the original preamble and 20 GPU dispatch boundaries. Prototype reuse of compiled CPU tapes with strict graph/descriptor identity checks and explicit invalidation; qualify <=16 first. See DESIGN.md for backend state and synchronization requirements. No installed components or Claude files changed.

## Replay prototype and new correctness finding

Replay implemented privately in replay-host; prepare_replay_host.py derives from unchanged q8 host. It retains normal preamble/transfer submission/partial-sum clear, uses fresh counters and command buffers, preserves captured per-segment submit/exit/almost-ready metadata, and restores backend end state. Exact metadata keys are about 196952 uint64 words (1.58 MB); full descriptor tables must match. Two repeated identical captures are required before hits. No replay of Vulkan command buffers.

Short qualification passed at 16 and 192: each 213 native records across two prompts, with 35 Roman and 30 C++ actual replay hits. Runtime diagnostics show one native preamble memory operation and zero native body operations in qualified captures.

Larger-context test (prompt151, prediction128, native KV256→512) FAILED against native. The first mismatch occurs at record1, target position151, before the KV transition. Replay and uncached parent produce identical complete audit SHA256 32f7b0e9760fe854bcc0aac4b014ee2f3b13be2fe9f24bd286b56f1c9dc63cc6; native is 5d3b420ece0f56fe972716dea0e1f3482eddd5026e1f9712f974a7f18cc2f871. Thus the observed mismatch is inherited from parent, not introduced by replay. Native-attention fallback (without_fa.comp) produces exactly the same parent hash, ruling out unified attention for this discrepancy.

Performance testing is STOPPED pending correctness diagnosis. Prepared scripts require boundary correctness and will not pass that gate. No variant adopted.

An initial KV trace parser checked the wrong field (N is flattened query count, ne2 is query count); corrected analysis confirms native KV256 and512. The failed parser run and subsequent mathematical comparison assertions were harness/quality failures, not GPU crashes. GPU children exited0; guards resumed the exact original waiter.

Next experiment: disable all optional mega host fusers on the same larger-context case. Running via guarded batch, session52906, boundary-no-fusions-run.log. If it matches native, bisect fusers; otherwise use per-operation verification and/or native repeat to isolate the first diverging operation. All evidence retained under boundary192.

## Correctness isolation update

Disabling all six optional host fusers, and separately adding a grid barrier before every recorded operation with fusers disabled, both produced the exact same failing parent audit hash on the larger prompt. Native FA fallback also gave that same hash. These controls do not support an attention/fuser/missing-grid-barrier explanation for this case. Individual native-versus-mega operation verification is running with prediction8, no optional fusers, replay disabled (session22566; boundary-verify1-run.log). It changes execution boundaries, so it is diagnostic only. Performance gates remain closed.

## Verifier harness issue and correction

The original per-operation verifier asserted at ctx->descriptor_set_idx < ctx->descriptor_sets.size() during common initialization, before producing comparisons. Its additional native dispatch did not reserve a descriptor. GPU child did not finish after the debugger exited or after SIGTERM; the exact owned PID979707 was killed with SIGKILL after checking executable, environment and assertion log. The guarded parent then resumed the exact original waiter. This was a CPU descriptor assertion, not a reported GPU device fault.

strict-verify-host now privately reserves a descriptor before the extra native dispatch, compares float bits exactly rather than with the old 1e-3 tolerance, and synchronizes diagnostic graphs before consuming readbacks. GPU shader unchanged. Build running: unifiedexec10912, strict-verify-build.log. Next guarded job is run_mtp_tape_replay_strict_verify16.py, prediction8 at 16 physical groups. No new GPU job launched until build completes.

## Current correctness follow-up

The strict verifier completed some per-op reports but hit its explicit 300s limit; guard terminated the diagnostic and resumed the original waiter. No complete per-op/native-prefix result is claimed. RMS order differences are directly reproduced in a focused microbenchmark. Native-order correction prototype is in isolated/mtp-native-rms-order; its v1 matched all nonzero patterns at128x48, leaving only signed-zero differences. V2 fixes the default identity post-scale signed-zero behavior and is compiling (session85203). See that project STATUS.md for next actions.
