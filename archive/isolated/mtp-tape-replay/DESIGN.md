# Target tape replay investigation

Status: observer implemented; replay NOT implemented or qualified.

## Evidence motivating this investigation

Historical native MTP trace `isolated/mtp-integration/native.tape`: ten steady 4086-node target graphs, each with 2147 dispatches. Nine adjacent comparisons found identical pipeline keys, workgroup sizes, push constants, and buffer tuples for every dispatch. See `../mtp-dispatch-coalescing/replay-input-audit.json`.

This does not establish invariance of current packed/fused mega records. The observer captures those records after fusion at each original flush and captures the entire 2048-slot descriptor range table. It counts native copy/fill operations outside the flush implementation and logs fallback/pending counts. No performance claim can be derived from file-I/O capture runs.

## Candidate design for later implementation

Preserve original GPU dispatch and submission boundaries. Reuse compiled CPU records rather than joining shader segments or replaying Vulkan command buffers directly. This avoids relying on command-buffer pending-state reuse and keeps the 20 target dispatches that outperformed joined execution.

Possible hit path: for each cached segment, restore already-fused records, invoke the existing tape upload/counter clear/dispatch/barrier implementation with fusion disabled for those prepared records, and submit through the existing context/forward helpers. Never reuse old dynamic counters. Preserve current parity, scratch pointer, descriptor set, tape offset and per-segment counter selection.

## Required audits before enabling replay

- Current mega records and referenced slot bindings must be invariant in actual model traces. Startup descriptor registration and fallbacks are not eligible.
- A graph fingerprint must cover node order, op, type, ne/nb, op_params, data, buffer identity/context, view offset/source, source topology and source metadata. Tensor contents are intentionally dynamic; inputs must still be uploaded normally.
- Descriptor identities and GPU allocations must remain live. Slot IDs alone are insufficient. Start conservatively with the full descriptor table in the identity check.
- Exclude any capture containing native memory commands, compute fallbacks, pending descriptors, replay verification, performance instrumentation, or unsupported context switches. Explicitly audit any CPU deferred memcpy/memset state carried into graph compute.
- Audit backend internal state that normal graph recording updates: last_total_flops, prealloc offsets, pipeline/tensor tracking, unsynced tensor lists, tensor_ctxs weak pointers, fusion scratch ownership, almost-ready/serialized fences, submit_pending and transfer synchronization.
- A hit path must preserve queued input transfers and process staging in/out lists through existing helpers. Do not clear pending contexts or submit fence state blindly.
- Cache eligibility should require repeated identical compiled records for an exact graph identity; changes invalidate and use the original path. Fingerprint equality is not a substitute for correctness qualification.
- Initially restrict to target decode graphs with exactly 64 GLU nodes and second dimension 1 or 2. Prefill and KV shape transitions must fall back. Broader support needs separate qualification.

## Qualification sequence

First launch at <=16 physical groups; compare both prompts against all 213 native full-vocabulary logits/hidden records and token/acceptance counters. Then qualify 192 within the existing approved residency bound. Add graph-shape/KV-boundary/rollback coverage before considering broader use. Measure CPU recording and synchronized target time, then symmetric asynchronous full-model throughput with telemetry. External compile interference invalidates adoption comparisons.

## Guardrails

All work private to megakernel-review. No installed driver, production launcher, Claude checkout, clocks, package or affinity changes. One guarded GPU job at a time. No replay performance or correctness claim has been made.

## Current observer result

At both 16 and 192 physical groups, Roman 37 and C++32 steady target graphs each had identical compiled 3440-record, 20-segment tapes and identical full slot tables within each run. All 213 native numerical records per group count passed. Each steady graph counted one native memory operation; source preamble clears prealloc_add_rms_partials before the main node loop (q8 host lines19214–19218). Identify its actual callsite and phase before relaxing rejection of native operations. A replay hit should occur after normal transfer submission/preallocation/partial clear setup, then bypass only node recording while preserving required backend state.
