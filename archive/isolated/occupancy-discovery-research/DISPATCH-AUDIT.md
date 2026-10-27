# Decode dispatch coalescing audit — initial findings

Source audited: isolated/q8-two-column-f32/ggml-vulkan.cpp. No host or shader implementation changed in this audit.

## Submission boundaries

- Graph compute uses FLOP thresholds (last graph / 40, capped), node thresholds, final node, and an almost-ready fence. Early FLOP boundaries explicitly end/submit contexts.
- ctx_end flushes pending mega records. build_graph ends and submits at requested boundaries.
- submit_after may synchronously wait/reset a serialized submission fence, resets first-node state, and scales FLOP thresholds. It cannot be reused as a virtual boundary without an actual submission.
- Almost-ready submission has an independent fence. synchronize waits/resets it only when pending. A coalesced final submission must preserve pending-fence bookkeeping.

## Native commands that require care

- ggml_vk_buffer_copy_async directly records vkCmdCopyBuffer; it does not itself flush pending mega records. Backend tensor copy calls it on a compute context.
- ggml_vk_buffer_memset_async directly records fillBuffer, or defers a CPU memset on UMA; it does not itself flush pending mega records.
- COUNT_EQUAL zeroes its output through that helper, then calls sync_buffers. With pending tape, sync_buffers appends a shader grid barrier instead of immediately flushing. Coalescing needs an explicit native-command ordering policy; do not rely on a barrier record to order an already-recorded Vulkan fill against deferred shader work.
- Preallocated ADD_RMS partials are cleared before graph processing. This must remain outside any previous pending tape.
- Direct copyBuffer/fillBuffer sites elsewhere still need a complete call-site audit before coalescing is enabled.

## Tape preparation constraints

- flush runs six fusers over the whole current tape. Coalescing must preserve the former segment-local fusion scopes, or independently prove fusers safe over new boundaries.
- Keep pending records visible to existing recs.empty checks and context-switch flush hooks.
- Replace removed segment boundaries with explicit global grid barriers; command-buffer ordering cannot simply be deleted.
- Ensure total record count fits segment counter stride (4032 records) and tape capacity after added barriers/fusions. Fall back to real flush when necessary.
- Decode-only graph qualification must use GLU batch dimensions, not arbitrary internal matmul dimensions. Exclude prefill and verification replay modes initially.

## Qualification before performance claims

First physical launch <=16 groups; native full logits/hidden/token comparisons; then approved resource/residency graduation to 192. Compare parent and discovery hosts separately using symmetric full-model controls. Existing parent kernel arithmetic and FA remain unchanged.
