# Next resource-pressure experiment

The CPU metadata cache reduces planning time but has no demonstrated throughput gain. Flat matvec indexing (including six preserved DontFlatten merges) passes both numerical depths but also has no gain. Keep the BF16-pair reference and investigate the monolithic kernel's resource limit next.

## Evidence and hypothesis

Historical isolation in resource-stats.json has native-FA-only at96VGPR and native-FA-plus-GDN at72VGPR. Thus GDN contributes to the register peak. Those historical end-to-end split modes were slower; do not adopt them or treat their omitted-native GPU timestamps as totals. The current full-FA phase shader is96VGPR/16KB LDS, pre-allocation VGPR91. Source op12 holds16 state floats per invocation plus Q/K temporaries. Reusing LDS for part of that state may lower the global VGPR allocation without changing lane/reduction arithmetic.

## Partial state storage in LDS

Derive from full256_fa_phase_bf16_pair.comp and current bf16-pair host, not the rejected bundle/cache/flat variants. Add a volatile float workgroup block at explicit offset0,2304 floats(9216bytes):9 rows *64lanes *4wave slots. This aliases existing scratch only between operators; full FA's current allocation already covers16KB, so this block should not raise LDS size.

Use address((vSlot*9+r)*64+gl_SubgroupInvocationID) for r<9. Other seven state rows stay in the original private array. Each invocation owns its own addresses, and wave slots have disjoint regions. No cross-invocation shared-state reads occur. Volatile shared accesses must survive SPIR-V/NIR so the compiler cannot simply promote the values back to private registers. Check qualifier support and actual generated accesses.

Preserve existing iteration/reduction order. Rewrite initial state stores, kv-shard reads, updated-state assignments and final/snapshot reads. For each update retain a local updated float, store it through the selected storage, and use that same float for attention accumulation; avoid an extra volatile reload there. Keep the original16-element private declaration initially and let unused first9 elements be eliminated; no out-of-range private indexes in unselected branches. Do not introduce workgroup barriers inside the guided GDN wave queue. All waves still join the existing main barrier. Both generic multi-token loop behavior and single-token frozen model must stay semantically correct.

First gate is a conservative64-group resource/output check. If VGPR allocation does not decrease, record the failed pressure hypothesis and avoid broader throughput testing. If it decreases, run both65-frame prompts before considering resource/layout/grid changes. No arithmetic approximation is intended.

## Further FA scratch reuse, if needed

QV0..8448 holds Q in QK and V in PV. Existing barrier before score store ends all Q/K reads. Scores can potentially use QV offset0, and P can use the now-dead K region8448..11520. However OUTPUT CANNOT ALIAS P: fa_output is written inside each HSV-tile iteration while P is still needed by later HSV tiles.

A conservative new layout is QV/Scores0; K/P8448; Output11520; Slopes13568; IQ13632; end13664(about14KB after driver allocation). Add a workgroup barrier after all score reads/P writes and before any V load overwrites QV/Scores. The existing source has no such barrier immediately after the P loop. Preserve the HSV-tile output storage and all existing barriers; do not alias output with V without separate lifetime proof. This layout experiment changes no arithmetic, but needs its own source audit, SPIR-V/resource checks and both output depths.

## Resident-grid gate

Do not increase the physical grid solely from these proposals. Check actual driver allocation, shader WGP/CU mode, active CU count and LDS/VGPR limits. Local Mesa compiler info defaults gfx12 to768 wave64 VGPRs/SIMD, allocation granularity12,16 waves/SIMD and two SIMD/CU, but kernel-reported device limits can override that default. WGP/CU scheduling changes how workgroup limits round. A lower VGPR count plus14KB LDS might allow a larger grid with headroom; that is not yet established for the actual shader. Never test at a guessed occupancy limit. Larger grids need conservative resource proof and long correctness checks before timing.

Full benchmarks must include deeper KV lengths if the additional FA barrier helps4K but could hurt long context. All changes remain isolated. No speed or quality claim exists for this unimplemented plan.
