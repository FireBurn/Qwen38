# Unified FA probability/output scratch reuse

Private derivative of qualified native_order.comp. Integrated FA and native RMS order retained. No driver, installed-stack, clocks, affinities or Claude changes.

## Changes

Scores and probabilities share8448..12544; rounded probabilities are staged in invocation registers, then a workgroup barrier finishes all score reads before probability stores. Output tiles move to dead V staging at0..2048, with a workgroup barrier after all cooperative V reads and another after output consumption before the next V load. SHMEM_STAGING must remain0, as in both existing captured FA keys. Slopes and IQ tables remain persistent outside the score region at12544 and12640. Metadata/dispatch keys unchanged.

Expected high-water12672bytes rounds to13312 at gfx1201's1024byte LDS granularity. The96VGPR register limit remains; no larger persistent grid authorized by the LDS reduction.

## Failed setups retained

- First attempt used the old default-precision FA client, whose native output differs from unchanged qualified F32 parent. Retained in first16-default-precision-invalid; it is not candidate evidence.
- V1 reused scores/probabilities but overlooked existing OutputStorage aliasing. Correct F32 controls passed, candidate failed: first64 head dimensions correct, later192 corrupted,18432/24576 words different. Output tile0 overwrote probabilities required by later HSV tiles. Saved source/SPIR-V/logs and diagnosis in v1-overlap-invalid. No model/192 trial was run on V1.
- V2 adds the separate output lifetime handoff described above. Shader rebuild terminal0; glslc/spirv-val/spirv-opt checks pass. Nonfatal allocator size-class messages were emitted during optimization.

## V2 qualification

- First16 session17026 terminal0: KV256/3328, head256,Qheads24,KVheads4,C1/C2 via batch-versus-serial, causal masks, original F32 native/parent/candidate bits all exact; no native dispatch fallback. Both candidate resource gates96VGPR,13312LDS,0scratch.
- Causal and model batch23947 terminal0: causal future mutation/restoration checks exact at both KV sizes. Full model mega16/head16 and mega192/head192 both canonical SHA873abacccc270bc1a0669f62ac831dcc14ace252db9f60bbc0006a7c7b84dec2,34tokens,19drafted/15accepted; full target logits, normalized hidden states and sampled draft10 ID/score bits unchanged. Same private threshold core/backend and frozen RADV.

## Running performance job

Session52691, run_private_guarded_batch.py: focused FA micro benchmark followed by512-token ABBA parent/candidate full-model comparison. Exact outputs/tokens/counters required, timestamps/clocks/load retained. Poll this same session; do not start another GPU job before it terminates. No speed claim yet.

## Terminal performance

Batch52691 terminal0. Focused192group FA benchmark micro-throughput/20261026T102830Z: parent3.0925ms,candidate3.0580ms per128-copy graph,1.116%lower latency, but parent drift1.125%,candidate0.847% and clocks differ. Not an established component win. Every output bit native-exact.

Longer full-model512-token ABBA paired512/20261026T102846Z/summary.json: parent43.6119,candidate43.5616t/s, candidate-0.115%. Parent drift0.555%,candidate0.280%; all513tokens and279drafted/234accepted counters identical. Zero compiler processes; CPU roughly5-8% in steady samples. No confirmed speed improvement. Keep as a correctness-qualified13KiBLDS layout experiment; do not promote. All own GPU jobs terminal at this entry.

Independent next control in ../mtp-fa-k-loop-roll: original native layout, only KQ feature loop Unroll->DontUnroll. No combined resource claim or shader scheduling flag changes.
