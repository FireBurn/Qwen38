# Combined smaller kernels: correctness and overlap

**All three candidates work together in the captured tests. No model speedup is established.** They are the explicit-shuffle native activation quantizer, local integer Q3 correction, and coalesced SwiGLU→Q8 shuffle fusion. The precomputed activation-sum sidecar is not included.

One private host supports all eight on/off combinations. All eight produce the same complete 32-requested-token model audit at a 16-workgroup fusion cap. Native versus all-combined also matches at the 136-workgroup cap intended for timing. All captured logits, hidden states, draft IDs/scores, tokens and counters match the reference. [Eight-arm comparison](../archive/isolated/native-combined/model32/comparison.json), [per-arm results](../archive/isolated/native-combined/model32/checks.json), [larger-grid comparison](../archive/isolated/native-combined/model136/comparison.json).

## Work accounting

| Captured 32-token workload | Native | All combined |
|---|---:|---:|
| Separate activation quantizer calls | 4675 | 3516 |
| Fused SwiGLU/quantizer calls | 0 | 1159 |
| Q3 matrix calls | 1560 | 1560 |
| Total dispatches | 47288 | 46129 |
| Barriers | 32406 | 31247 |

Fusion removes 1,159 separate SwiGLU dispatches and 1,159 barriers. It replaces 1,159 of the original quantizer calls, leaving 3,516 for the standalone quantizer change. No duplicate quantization appears. Quantizer/Q3 toggles preserve normalized dispatch order and barrier counts within each fusion setting.

The overlap matters: the standalone quantizer change and fused quantizer affect some of the same work. Their estimated gains cannot be added as independent percentages. The Q3 correction changes matrix arithmetic without adding a new activation buffer. [Implementation and accounting notes](../archive/isolated/native-combined/STATUS.md).

## Longer captured prompts

Six additional arms compare native, fusion-only and all-combined on coding and maths prompts, each requesting 128 tokens at a 136-workgroup fusion cap. All complete audit bytes, generated tokens and acceptance counters match the preserved native references. No new target-driver faults were recorded.

| Prompt | Predicted | Drafted | Accepted | Combined fused / separate quantizer calls |
|---|---:|---:|---:|---:|
| Coding | 130 | 68 | 62 | 4001 / 12140 |
| Maths | 129 | 69 | 60 | 4059 / 12316 |

Fusion-only and all-combined keep the same normalized dispatch sequence and barrier counts. These are 128-generated-token checks with a 4096 context limit; they are not stress tests of a populated long KV context or general quality claims. [Comparison](../archive/isolated/native-combined/prompts128/comparison.json), [results](../archive/isolated/native-combined/prompts128/checks.json).

## Production compatibility boundary

The production snapshot and Claude's observed source tree share the quantizer and SwiGLU sources with the frozen backend. Other matrix code and the host differ; the production snapshot includes newer Q4/Q5 paths. Independently compiling the three reference and three candidate Q3 reduction variants with production-snapshot includes produces byte-identical modules to those tested here. This supports shader compatibility for those exact defines, not current-production host/pipeline/core or model qualification. Claude's files were read only. [Source hashes](../archive/isolated/native-combined/production-source-audit.json), [six-module compilation checks](../archive/isolated/native-combined/production-q3-modules/checks.json).

## Timing status

A 16-arm 512-token comparison is queued: all eight settings forward/reverse on the identical combined host. It waits for successful completion of the earlier serialized timing workflows, then applies the existing CPU/build/clock gates. It checks every generated token and acceptance counter and rejects steady-phase sensor errors or monitor failure. Synthetic checks execute the actual monitor and validity expression. Queue readiness is not a timing result. [Monitor checks](../archive/isolated/native-combined/telemetry-tests.json).

Longer KV contexts, current-production model qualification and quiet timing remain required before adoption. No faster-than-native mega kernel or combined native path is established.
