# Native Q3 integer correction experiments

**The native Q3 candidate passes the captured model audit. No speedup is established.**

The original Q3_K shader unpacks positive 0..7 bytes, recenters them to −4..3, then computes packed integer dots. The candidate leaves the weight bytes positive and subtracts four times the corresponding 16-value activation sum from the integer dot result. Both forms produce the same integer before the original floating-point scaling. The candidate requires no additional buffer or descriptor.

## Actual native shader

All three unchanged reduction variants compile byte-identically to the frozen backend modules. A private default-off host selects the candidate once per device and uses the original lazy pipeline factory. Quantizer format, matrix geometry, cache, dispatch ordering and barriers remain unchanged.

| Columns | Reference → candidate instructions | Code bytes | VGPRs | VMEM instructions |
|---|---:|---:|---:|---:|
| 1 | 2272 → 2226 | 12944 → 12660 | 48 → 48 | 128 → 128 |
| 2 | 3528 → 3495 | 20328 → 20172 | 48 → 48 | 207 → 207 |

LDS, scratch and spills remain zero. These are compiler counts, not runtime speed measurements. C2 VALU instructions actually increase from 2201 to 2202, despite the lower total instruction count. [Resource evidence](../archive/isolated/q3-native-correction/operator-resources/resource-comparison.json).

C1/C2 focused operators with Q3_K, Q4_K, Q5_K and Q4_0 consumers match output bytes. [Checks](../archive/isolated/q3-native-correction/operators/checks.json).

Native, candidate and candidate with bounded head match the complete captured 32-requested-token audit: 34 predicted, 19 drafted, 15 accepted. All captured logits, hidden states, draft IDs/scores, tokens and counters match. The candidate substitutes 1,560 Q3 dispatches with identical normalized dispatch sequence and barrier count. This does not establish correctness for all prompts, longer contexts or the current production stack. [Model comparison](../archive/isolated/q3-native-correction/model32/comparison.json), [per-arm checks](../archive/isolated/q3-native-correction/model32/checks.json), [implementation notes](../archive/isolated/q3-native-correction/STATUS.md).

## Precomputed activation sums: separate feasibility test

A second idea computes those half-sums once in the activation quantizer and reuses them across output rows. It needs four additional bytes per 32 activation values: an 11.11% increase in packed activation storage, not in model weight storage. It could remove repeated row-local correction work, but adds quantizer writes, a matrix buffer read and host/cache plumbing.

The isolated integer-dot GPU probe compared four forms:

| Form | Instructions | Code bytes | VGPRs | VMEM instructions |
|---|---:|---:|---:|---:|
| Packed recenter reference | 92 | 500 | 24 | 4 |
| Local correction | 88 | 476 | 24 | 4 |
| Precomputed binary16 sum | 93 | 496 | 24 | 5 |
| Precomputed signed-int16 sum | 84 | 448 | 24 | 5 |

The signed-int16 form avoids conversion and dynamic half selection. All 768 capped wave64 GPU cases match an independent scalar oracle, with intact guards and no new target-driver errors. CPU tests separately cover 1.6 million packed comparisons. These are isolated integer-dot results; the precomputed-sum approach has no native matrix/quantizer integration or model qualification. [GPU evidence](../archive/isolated/q3-activation-sidecar/diagnostics-int16/checks.json), [CPU packed checks](../archive/isolated/q3-activation-sidecar/packed-proof.json), [notes and costs](../archive/isolated/q3-activation-sidecar/STATUS.md).

Earlier mega-kernel work already reused correction sums within workgroups across two/four rows. Small local gains failed to improve model speed. The new native local-correction candidate therefore still requires measured full-model benefit. Computing a sum once across all output rows is a distinct unqualified proposal, not evidence that combining earlier changes will produce additive gains.

## Timing status

A serialized eight-arm 512-token workflow now compares native quantizer off/on and Q3 correction off/on, each against its own identical host control. It waits behind the earlier fusion timing workflows and retains CPU/build/clock gates. It checks generated tokens and counters, records idle sensor errors and rejects steady-phase sensor errors. No combined mode is implemented. Queue records are historical readiness evidence, not proof that timing ran. [Queue setup](../archive/isolated/NATIVE-SHADER-PERFORMANCE-QUEUE.md), [actual-monitor synthetic tests](../archive/isolated/native-shader-telemetry-tests.json).
