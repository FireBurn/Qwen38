# Publication snapshot

Captured at 2026-10-27T21:28:15.763966+00:00.

## Qualifications

SwiGLU→Q8 fusion is model-audit exact at16/192/256/320 workgroups. Prefix claims and Q6 one-row are also model-audit exact through320 with the two-dword copy override. These are correctness results, not speedups.

## Fresh mixed-matrix benchmark

Status: **partial operator comparison; not a complete paired result**. 13/16 arms recorded.

The queue stopped when CPU load invalidated a later arm. Invalid arms are excluded from the means below; the overall paired result is incomplete. All recorded outputs match. Same copy2 override in every arm. This is not a model-speed result.

| Timing | Mode | Valid arms | Mean µs/graph |
|---|---|---:|---:|
| batch | native | 2 | 808.479 |
| batch | parent320 | 2 | 1003.056 |
| batch | prefix320 | 2 | 1000.742 |
| batch | one320 | 2 | 996.125 |
| single | native | 1 | 1538.294 |
| single | parent320 | 1 | 1749.402 |
| single | prefix320 | 1 | 1750.004 |
| single | one320 | 1 | 1741.329 |

Evidence: [checks](../archive/isolated/mtp-quant-schedule-timing/stream-bench/20261027T211915Z/checks.json). A single arm is not a forward/reverse estimate.

## Still pending

- Remaining quiet model and FA comparisons were not executed by this portfolio after its microbenchmark validity failure.
- The follow-up candidate512-token comparison stopped at its first native arm because CPU load invalidated the measurement; no paired result was obtained.
- A general fix and broader qualification for the four-dword copy failure.
- Current production`.27` comparison before adoption.

Queues continue independently of publication; future results are not implied by this snapshot.


## Native-path SwiGLU→Q8 prototype follow-up

This is a separate, default-off native-backend prototype, not the already-qualified mega-kernel fusion above.

- Focused native-versus-fused C1/C2 tests pass byte-for-byte for all 64 floating SwiGLU and downstream Q4/Q5 matrix outputs across four input cases. The fused pipeline uses 48 VGPRs, zero LDS and zero scratch. [Operator evidence](../archive/isolated/native-swiglu-q8/operator-host16/checks.json).
- The 16-workgroup model test preserves generated tokens and counters (34 predicted, 19 drafted, 15 accepted), but **fails the complete byte audit**. Off SHA-256 is `873abacccc270bc1a0669f62ac831dcc14ace252db9f60bbc0006a7c7b84dec2`; both fused variants produce `933f5338802427c5e26fdb7c10621c37f78bea4c1c166a57bfd9df9edbbe2145`. [Model evidence](../archive/isolated/native-swiglu-q8/model16/checks.json).
- The model mismatch remains unexplained. The prototype is unqualified and no throughput improvement is claimed. Component equality is insufficient to promote it.

## Native fusion diagnosis resolved

The earlier failure above is retained as history. Matching native’s `glslc -O` compilation fixes the quantization rounding discrepancy. Focused operators and full captured model audits now pass at 16 and 136 workgroups. No speedup is established; quiet timing and current-production comparisons remain pending. See the [diagnosis and evidence](NATIVE-FUSION.md).

## Metadata-node fusion coverage

An opt-in planner extension increases target coverage from 14 to 56 pairs per graph. Captured model audits pass at 16 and 136 workgroups with and without the bounded head. No throughput result yet. See the [expanded coverage report](NATIVE-FUSION.md#expanded-coverage-across-metadata-nodes).

The expanded-fusion 512-token off/adjacent/expanded comparison is now queued after the standalone component test. Neither has a timing result yet; the follow-up requires a complete valid predecessor result before starting.

## Deferred-only barrier follow-up

The guarded barrier candidate passes focused four-quant tests and captured model audits at 16/136 groups. It removes 1159 recorded barriers with identical normalized dispatches; physical GPU savings remain unmeasured. The serial512 queue is updated to four matched-host modes including this candidate. See the [fusion report](NATIVE-FUSION.md#conditional-barrier-coalescing-and-planner-overhead).

## Longer prompt and transfer-path follow-ups

Two additional prompts pass six128-requested-token native/coalesced/bounded arms. SDMA opt-in passes144fresh-process transfer cases and the captured16-workgroup model audit; it remains experimental and separate from timing. A read-only load sample attributes most observed CPU activity to plasmashell. Timing remains pending under unchanged gates. See [fusion](NATIVE-FUSION.md) and [SDMA](SDMA.md) reports.

## October28 resume

The prior component timestamp job finished its output checks but failed telemetry before recording any samples; its timing is rejected and its full512follow-up did not start. A robust monitor is now queued with stricter per-arm coverage. Explicit shuffle8variants report24VGPRs and pass captured native-model audits at16/136groups in wave32/wave64, with zero new driver faults. Their timings are queued after the resumed predecessor. The negative default-copy path is quarantined after a retrospective ring-timeout correlation. [Details](SHUFFLE8.md).
