# Integration constraints and route

The original prototype is exact top1. A separate complete GPU top10 pipeline now passes small and full-vocabulary tests (gpu-topk-micro/full); its seed scores, survivor scores and ordered top10 agree with native Q8, including tested ties and empty/fewer10 cases. Neither path may expose its pruned full score vector through a full-logit API. The saved37-40% top1 gain and top10 timings are head-only under external compilation.

## Existing graph support can preserve the fallback

`llama-graph.cpp::build_sampling` already uses `ggml_build_forward_select` to select original full logits or backend sampling results. The greedy backend can produce candidate IDs plus one original Q8 score per query, following the existing partial sampled-logit/candidate contract. Keeping `data.logits` pointing at the original view would force the dense head to execute and erase savings. An optimized result must replace sampled logits and candidates together; original `res->t_logits` remains the raw branch.

A private backend graph-construction export could build the coarse/filter native GGML graph followed by a backend-supported `GGML_OP_CUSTOM` node for compaction, sparse original-Q8 scoring and candidate-only reduction. The custom node must encode into the current command buffer, never call graph compute or the submitted-context prototype recursively. The custom node's dependencies must be weights, selected normalized hidden input, filter mask and caller-owned workspace, with no dependency on dense full logits. One batched node must serve both C2 queries; per-row callbacks must reuse it. Custom-op recognition must use a checked private marker/procedure identity and validated shape/type/layout, not a tensor name alone. Cache ownership, descriptor cleanup and graph reuse need explicit handling.

Before integration, factor encode-only operations out of the tested prototype without changing synchronization semantics. Qualify the standalone custom graph first at <=16 physical groups, inspect resource use, then qualify 192 groups and changing-input graph reuse. Preserve full-logit fallback and native original-Q8 score order. Restrict the coarse F32 selection override to the private coarse head; its current all-Q4 C<=2 condition is unsuitable for a real model.

## Sampling eligibility

Pure raw greedy is the first eligible backend sampler. The usual temp0 chain may have preceding logit bias, grammar, penalties, DRY or other transforms; do not bypass them based on temperature alone. Any unsupported transform must keep the original graph.

MTP draft currently computes TopK10, sorts candidates, logs three, picks the first and checks p_min. With p_min=0, the confidence check cannot reject a finite probability, so exact top1 can preserve drafted tokens; such a branch still needs explicit eligibility and diagnostic behavior handling. Otherwise exact top10 and confidence semantics must remain intact. The complete GPU top10 path now supplies exact IDs and original scores for all10 candidates, preserving the native backend TopK partial-logit/candidate interface on tested inputs. It still needs model integration and confidence/acceptance verification.

## Required end-to-end evidence

Reproduce native token streams and MTP acceptance on full model inference, exercise raw/full logits fallback and unsupported sampling transforms, compare same-stack native and mega modes with interleaved whole-model benchmarks, and repeat without external compile interference. Head-only savings do not prove aggregate token throughput or that the mega kernel beats the production baseline.

## Residual cascade experiment

`analyze_cascade.py` tests a second filter reading only first-pass survivors. Quantize A-B with FP16 per32 scales: one sign bit using mean absolute residual, or two bits using four symmetric half-integer levels. Each row stores an upward-rounded residual norm for A-B-correction. The second upper bound is coarse score plus correction dot plus residual-norm times hidden-norm and a floating-point error allowance. Exact original Q8 still evaluates final survivors. This adds no approximation to the required final token selection, provided GPU bounds/arithmetic are qualified. Traffic estimates alone do not justify adding a kernel.

## Current performance choice

The matched five-mode transfer control shows C1 bounded top10 faster than both tested native references under load, but C2 bounded top10 slower than native GPU top10. Keep native C2 top10 as fallback while integrating and measuring C1. Packing results is also a native optimization, so compare against native packed results as well as the actual production CPU sampler. Top1 remains a distinct optimization opportunity for eligible pure greedy consumers. Complete top10 GPU test path uses multiple submitted contexts, not a single scheduler custom graph op; encode-only factoring is still needed for graph integration. Test-only forced CPU mask writes require an explicit synchronize before tensor_set: tensor_set alone did not prevent pending GPU overwrite.

## Graph recording qualification

`topk-graph-host` and `head_bound_topk_graph_micro/full` now qualify the final compact/sparse/top10 stage as a private custom graph node. The node records into the outer command buffer and returns real I32 IDs to a downstream GPU copy. This is not the whole head in one graph: seed and correction still submit separately, using a temporary GPU mask bridge to prevent upstream recomputation. Micro and full tests cover changing inputs and native bits, including actual applied forced masks. Configuration lifetime is caller-owned through final sync; full scheduler allocation/reuse and mega-active cases remain unqualified. The next graph stages should expose seed32 F32 scores and corrected F32 mask as direct outputs, then remove the bridge and staged APIs from the normal execution path.

## Complete head graph now qualified

`head-graph-host`, `head_bound_single_graph_micro/full` and `head_bound_single_graph_bench` connect all stages in one graph. Seed scores and corrected mask are actual graph outputs, and the temporary bridge is removed. Both C1/C2 show substantial head-only gains versus native packed GPU top10 in the latest under-load benchmark; the earlier staged C2 slowdown is historical, not evidence against this graph path. Full model integration remains incomplete.

For model cache binding, a shape/name check is insufficient: another model can have the same Q8 head shape. Verify actual loaded head bytes against the original SHA before enabling fixed coarse/residual metadata; otherwise fall back. Keep additional GPU weight buffers and immutable custom-node configs alive through the last graph use and synchronization. Only raw unmodified output-head logits entering TopK10 are initially eligible. Native raw logits and unsupported shapes/transforms remain the existing graph branch. Prefer a private core library copy with an isolated sampler TU/relink over editing the frozen source/build used as controls.
