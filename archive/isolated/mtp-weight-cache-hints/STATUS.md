# Immutable weight temporal hint experiment

Hypothesis: keep streaming quantized weights from polluting near caches while retaining regular temporal behavior at the last cache level. Private SPIR-V candidate only; no installed driver/source changes.

build.py derives from the verified native-order RMS shader, changes only OpLoad MemoryAccess Nontemporal(4) for unambiguous pointers rooted in immutable quantized weight descriptors. 1558 static SPIR-V loads modified. Four selected descriptors are unused after optimization. spirv-val Vulkan1.2 passed. transformation.json records every instruction before/after. FA/KV, activations, stores, synchronization and arithmetic untouched.

Local Mesa vtn_variables.c maps SpvMemoryAccessNontemporal to ACCESS_NON_TEMPORAL; ac_shader_util.c GFX12 loads map that to near_non_temporal_far_regular_temporal, except SMEM. This is a retention hint, not a weakened fence.

probe16 completed terminal0. Q5_K K5120 R4097 C2 with four patterns and three bias cases native bit-exact, last16 graphs zero native dispatches. Parent and candidate resources both96VGPR,1spilledSGPR,16KiBLDS,0scratch,code493996bytes. Final ACO hardware-instruction programs identical after removing1064 cache-hint annotations. This driver lacks machine-code disassembly; no decoded binary claim. aco-hint-proof.json.

Full model16 passed all195 genuine native records,130tokens,65/65MTP accepted, no native fallback in last12 graphs; SHA5d3b420ece0f56fe972716dea0e1f3482eddd5026e1f9712f974a7f18cc2f871. Model192 currently running under guarded session52736. No speed claim. Next micro192: eight Q3_K matrices total306380800weightbytes, ABBA GPU timestamp comparison with clock telemetry. Full throughput comparison still required.

Model192 also passed genuine native195 records, tokens/counters exact, no last12 native fallback. Both model jobs terminal0. Micro192 terminal0: control0.7815ms, hint0.7970ms(mean1.98%slower), control drift6.08%, candidate drift3.58%, clocks1680/1688/1674/1781MHz across ABBA. No reliable speed effect, no adoption; micro192/validity.json.

Full asynchronous six-arm comparison running session7408: native24, native-order mega, weightNT, weightNT, native-order mega, native24. Driver/core/Q8 policy fixed; per-run telemetry captures clocks, compiler count and CPU load. This experiment does not enable replay, so it isolates shader policy. Scope is under-load diagnostic until clock/control drift and quiet validation pass. throughput-run.log authoritative. No throughput result yet.

Six-arm asynchronous diagnostic terminal0. Native28.564t/s, unhinted native-order mega23.4245, hinted23.3435. Hint -0.3458% vs mega; candidate drift2.2133%, native controls0.056%, mega controls0.115%. Clocks1661–1687MHz and13–16external compilers. All129tokens and74drafted/55accepted identical. No gain established; set aside. Throughput validity.json records interpretation. No own GPU job remains.
