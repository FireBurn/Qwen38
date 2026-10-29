# Native command recording: observation before reuse

The observer finds substantial repetition while preserving native arithmetic, including across a real KV-size transition. It establishes **no new throughput gain and performs no replay**. Both [qualified native configurations](CONTRIBUTION.md) remain unchanged.

The hypothesis is to reduce repeated CPU planning/recording while retaining separate native shaders and their resource allocation. Historical `mtp-tape-replay` work cached CPU-compiled **mega** tapes; it did not test retained native Vulkan command buffers, and its saved mega references must not be substituted for native ground truth.

## Implementation and scope

A new private backend copies the qualified guard-v2 source, rebuilds all three host translation units and links a separate observer object. Shader objects, backend-context layout and original GPU commands are unchanged. The harness uses a standalone process-only competition helper, without importing historical experiment setup code.

Each graph records native pipeline/layout/descriptor-set handles, workgroup dimensions, descriptor buffer/offset/range tuples and full push-constant bytes. It also records covered barriers, fills, copies, events and sequence boundaries. Submission command-buffer handles, fences and timeline metadata are stored separately. Unsupported commands receive explicit markers.

A “program” here is a canonical TLV representation of **captured command arguments**, not opaque driver command-buffer storage or shader code. Exact matches compare complete byte vectors within context/node-count/buffer-generation/entry-state groups. FNV64 is only a displayed index; a separate parser checks raw lengths/hashes and field counts. Raw metadata traces remain local, with SHA manifests archived; tensor contents are not captured.

Observer I/O changes CPU/GPU timing, so timings from these runs cannot establish a performance gain. Outside-graph uploads/transfers, debug labels, pool ownership, descriptor lifetime and GPU completion remain outside any replay proof. Zero recorded entry flags do not prove the GPU is idle. No commands are skipped or reused.

## Checks and observations

| Observer case | Graph executions | Unique captured programs in process | Exact repeat graphs |
|---|---:|---:|---:|
| Short prompt, 32 requested tokens | 61 | 9 | 52 |
| Coding, 128 requested tokens | 208 | 9 | 199 |
| Math, 128 requested tokens | 211 | 9 | 202 |
| Populated KV, 64 requested tokens | 122 | 19 | 103 |
| Boundary case, 128 requested tokens | 223 | 12 | 211 |
| Total across five processes | 825 | 58 | 767 |

All requested target-logit rows, generated tokens and draft/accept counters match their native references. Short, populated-KV and boundary cases run fresh stock400 controls; coding/math compare against the previously established native target-logit references. All observer storage completes, no unsupported-command markers occur in these graph scopes, and there are no new GPU errors. This covers 530 target-logit rows across the five observer cases; it does not capture every hidden/draft tensor or establish arbitrary-context behavior.

The boundary case spans target positions **174–302**, with 146 full-vocabulary target rows and audit SHA `16a693b0d912e151df9dc942bfb174f1dd5f8c48748f356b07be7cc8f2fa2f49`. Captured Flash Attention push constants explicitly contain `KV=256` and `KV=512`; the split-K reduction count changes between 4 and 8. Header field mappings are pinned by hash. This is actual recorded dimension evidence, not merely an assumed transition from token positions.

Across comparable adjacent graph pairs, **525,168 of 525,200 dispatch argument records match exactly**. The 32 differences are attention/reduction dispatches at the boundary. This supports investigating shape-aware reuse or cached planning, while demonstrating why shape/buffer invalidation is necessary. Repetition alone is not a lifetime or synchronization proof.

The full weighted trace contains 592,346 dispatches. Within command-buffer boundaries, 64,369 consecutive pipeline arguments repeat and 54,141 push-constant updates repeat with the same layout; consecutive descriptor-set/layout pairs do not repeat. These are potential redundant host API calls, not measured savings. The driver may already deduplicate them. [State-argument counts](../archive/isolated/native-command-observer/state-redundancy.json).

## GPU-driven scheduling capability check

A read-only physical-device query, using the pinned private RADV library, reports R9700/GFX1201 support for `VK_EXT_device_generated_commands`, including compute pipeline binding, and for descriptor buffers and buffer device addresses. It does **not expose `VK_AMDX_shader_enqueue`**. The query creates no logical Vulkan device and submits no GPU commands. This is specific to the recorded driver, not a claim about every driver or the hardware's capabilities through other APIs.

Device-generated commands are not a drop-in whole-model scheduler. The base token stream provides shader/push-constant/dispatch selection, rather than this backend's ordinary descriptor-set binds and barrier stream. [Vulkan token reference](https://docs.vulkan.org/refpages/latest/refpages/source/VkIndirectCommandsTokenTypeEXT.html).

Compute dispatch sequences have implied unordered execution; dependent model operations cannot simply be concatenated into one execute call while assuming their existing ordering and memory dependencies. [Execution rules](https://docs.vulkan.org/refpages/latest/refpages/source/vkCmdExecuteGeneratedCommandsEXT.html). Execution sets also require compatible pipeline layouts. [Extension design](https://docs.vulkan.org/features/latest/features/proposals/VK_EXT_device_generated_commands.html).

The inference from these rules is to prioritize ordinary native planning/recording reuse first. A generated-command path would need an explicit resource-binding and dependency design, followed by its own numerical and performance qualification. No such path was implemented or measured here.

## Next implementation decision

Profile fusion selection, alias/dependency analysis and driver recording separately before building a cache. A first cached host-plan prototype can retain normal native helpers and submission ownership; retained command buffers require additional pool, fence, descriptor and resource-generation work. The current backend normally records one-time command buffers and later resets their pool, so changing a begin flag alone is insufficient.

Any candidate must preserve uploads, preamble fills, current timeline values, backend tracking and invalidation on graph/shape/alias/allocation/context changes. Validate fresh native outputs, populated KV, bucket transitions and rollback before uninstrumented matched-load timing. The existing faster native configurations remain the baseline; no faster mega/FA kernel is established.

Evidence: [combined observer summary](../archive/isolated/native-command-observer/summary.json), [implementation patch](../archive/isolated/native-command-observer/observer.patch), [source/build provenance](../archive/isolated/native-command-observer/build.json), [boundary analysis](../archive/isolated/native-command-observer/boundary128/trace-analysis.json), [capability query](../archive/isolated/native-command-observer/capabilities.json), [observer plan](../archive/isolated/native-command-observer/PLAN.md).
