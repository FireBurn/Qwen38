# Current experimental full-FA reference

Shader: `../mk/gen/full256_fa_phase_no_descriptor_probes.comp`, with its `.spv` and `.ops`. Host: `../preserve-nq-counters/bin/libggml-vulkan.so.0.24.0`. Evidence/hashes: `../no-descriptor-probes-evidence.json`. Prior reference: SHARED_BINDING_REFERENCE.md.

Use256 physical threads,192workgroups. Set GGML_VK_MEGA to the absolute shader .comp path, GGML_VK_MEGA_WGS=192, and each of GGML_VK_MEGA_SHARED_LAYOUT, GGML_VK_MEGA_SEGMENT_COUNTERS, GGML_VK_MEGA_FUSE_NORM_QUANT, GGML_VK_MEGA_NQ_PRESERVE, GGML_VK_MEGA_FUSE_NORM_SCALE, GGML_VK_MEGA_FUSE_GDN_GATES to1. LD_LIBRARY_PATH selects the host above then isolated/build/bin. Native Vulkan/libc++; preserve R9700 device/queue/suballocation settings from checked runners.

## Evidence

- All typed descriptor aliases share binding1.149 old dummy length probes removed; real accesses and local mask-array length retained. Saved range audit proves their UINT_MAX sentinel false for captured shapes.
- Safe LS32 cache-writer mapping, cooperative-matrix FA with phase-reused shared memory, broader preserve-float RMS/Q8 fusion and other verified fusions remain.
- Both9-frame and both65-frame prompts are bit-identical to native-subgroup control.
- Separate coverage:70graphs; last32decode graphs have zero native operations, including FA. Initial slot-learning fallback still exists.
- Actual allocation96VGPR,0VGPRspills,24spilledSGPR,16KB LDS,240940bytes code.
- 4K-depth ABBA n96/r3:28.954476 vs28.789454(+0.5732%). Longer n256/r4:28.967436 vs28.769529(+0.6879%). These are paired gains over the preceding shared-binding reference, not comparable absolute speeds across earlier batches.

Still not faster than stock. No installed binary, launcher or Claude files changed. Frozen ABI0.24 Qwen3.8-27B/Q8KV/4K experiment; current-production baseline, natural-text likelihood/PPL, rollback, speculative batches and other shapes remain unqualified. Only one private GPU runner at a time. No runner remains active.

## Negative follow-ups

Readonly gamma has no gain. Selective small-task spreading is1.96% slower. A descriptor-only diagnostic reproduced reused VkBuffer handles changing BDA; the physical-slots-lifetime host invalidates old cached addresses and slot keys on buffer creation. It completes formerly failing repeated timing but is9.54% slower. Do not substitute any of those candidates. The delayed BF16-pair direction needs alias/liveness proof; see ../BF16-PAIR-NEXT.md.
