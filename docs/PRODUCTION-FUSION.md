# Smaller fusion on the production backend

**SwiGLU→Q8 fusion now passes the captured production target-logit audit, both alone and together with the quantizer/Q3 changes. No speedup is established.** This is the preserved production `aa8ab0504` GGML 0.27 / llama-common 0.7 stack, using the private Mesa driver and copy2 path.

The private port recompiles all three Vulkan host translation units against the same modified private context header. Generated shader-array objects remain unchanged. Claude's source and build outputs were read/copied only. Context cleanup synchronizes pending GPU work before destroying the custom pipeline. [Build proof](../archive/isolated/production-native-fusion/host/build.json), [implementation notes](../archive/isolated/production-native-fusion/STATUS.md).

## Stock eligibility is preserved

Production RDNA4 uses a float activation path for some single-column Q4/Q5 operations. The planner reuses the actual native MMVQ eligibility decision before deferring SwiGLU. It does not force quantization merely to enable fusion.

Twelve focused operator arms pass: two consumer orders × C1/C2 × native/fusion-only/all-three. They cover 64 SwiGLU pairs, four patterns and Q3_K/Q4_K/Q5_K/Q4_0 consumers. All output bytes match their own native control, with identical fast/legacy plans and no new target-driver errors. The fused wave64 pipeline uses 24 VGPRs with zero LDS/scratch.

Putting Q4 first after SwiGLU supplies a negative control: C1 correctly produces **zero fused calls** and retains exact output. C2 remains eligible and exact. Putting Q3 first permits fusion in both column settings. [Q3-first results](../archive/isolated/production-native-fusion/operators/checks.json), [Q4-first results](../archive/isolated/production-native-fusion/operators-q4-first/checks.json).

## Model audit

Native, fusion-only and all three changes together match the unmodified production target-logit reference:

- 38 full-vocabulary target-logit rows across 20 target batches;
- 37,745,416 captured bytes, SHA-256 `75055a49a5844ad14030f45cb76c11de20a44a6bb0e2db7c1c89a616137eb576`;
- all 34 generated token IDs, 19 drafted and 15 accepted;
- 1,159 actual fused calls and 1,159 conditional barrier coalesces per enabled arm.

These captures use a 16-workgroup fusion cap and the stock activation policy. Each arm completes 61 graph planner equality checks, with no deferred SwiGLU left unconsumed at graph end and no new target-driver errors. [Results](../archive/isolated/production-native-fusion/model32/checks.json), [comparison](../archive/isolated/production-native-fusion/model32/comparison.json).

The audit captures requested target logits, not hidden states or internal draft-score bits. Larger fusion grids, longer prompts/contexts, all eight production combinations and matched full-model timing remain pending. Existing non-fusion production timing is queued separately; queue readiness and raw operator times are not performance evidence. No faster-than-native mega kernel or production model is established.
