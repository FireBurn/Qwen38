# Current experimental full-FA reference

Shader: `../mk/gen/full256_fa_phase_shared_binding.comp` with its `.spv` and `.ops`. Host: `../preserve-nq-counters/bin/libggml-vulkan.so.0.24.0`. Manifest: `../shared-binding-verified-manifest.json`.

Use 256 physical threads and 192 workgroups. Enable GGML_VK_MEGA_SHARED_LAYOUT, GGML_VK_MEGA_SEGMENT_COUNTERS, GGML_VK_MEGA_FUSE_NORM_QUANT, GGML_VK_MEGA_NQ_PRESERVE, GGML_VK_MEGA_FUSE_NORM_SCALE and GGML_VK_MEGA_FUSE_GDN_GATES, each set to 1. GGML_VK_MEGA names the absolute .comp path; GGML_VK_MEGA_WGS=192. LD_LIBRARY_PATH selects the host directory above followed by isolated/build/bin. Preserve the R9700 visibility/queue/suballocation settings in the checked runners. Native Vulkan/libc++ only.

## Evidence

- One typed descriptor array replaces 42 identical arrays; tape retains binding 0, typed aliases share binding 1. The original host metadata header drives layout/pool/update counts without a host ABI change.
- The LS32 Q8 cache writer uses its original static virtual-workgroup assignment. Nine LS64 wrappers retain the guided queue. See ../SCHEDULER-SLOTS.md; historical blanket-guided derivatives had duplicate identical writes and are withdrawn as adoption candidates.
- Both nine-frame and both 65-frame prompt checks are bit-identical to the correct native-subgroup control. The corrected cache-writer source is identical to that control's wrapper.
- A separate 64-step long-prompt native-dispatch trace has 62 graphs entirely in the mega shader. The initial graph falls back while learning slots; graph 4 falls back for 16 FA operations on new KV descriptor ranges. The last 32 graphs have zero native operations. FA is included in the mega shader, with bounded descriptor-learning fallbacks.
- Real driver allocation: 96 VGPRs, zero VGPR spills, 42 spilled SGPRs, 16 KB LDS, 235948-byte code.
- First 4K-depth n256/r4 ABBA: 29.104420 versus corrected control 28.758740 (+1.202%). Quiet repeat: 29.113776 versus 28.795235 (+1.106%). Recent stock anchors: 31.936948 and 31.726929. Still slower than base.

No installed binary, launcher or Claude source was changed. No GPU runner remains active. This is a frozen Qwen3.8-27B/Q8-KV experiment using captured ABI0.24, not a latest-production qualification. Natural-text likelihood/PPL, state rollback, speculative-batch equivalence and other model/shader shapes remain outstanding before adoption.

## Negative results from the latest round

Preserving raw matvec outputs increases matvec/add fusion to 28 pairs per decode step, but the longer batch does not show a speedup. Row-wise gate/up/SwiGLU fusion and Q3 activation-load reuse pass output checks after fixing a local-result handoff error, but are slower. Keep those separate libraries/shaders as research artifacts.

Assigning initial tasks directly and skipping a main-loop barrier before a grid barrier also pass both regression depths, but were slower in the longer batch. The LS32 correctness repair is retained independently of those optimizations. See ../microbench-scheduler-4k/summary.json.

## Next direction

Read ../PHYSICAL-SLOT-PLAN.md before trying direct GPU addresses. The historical fullbda prototype excludes FA, loses current fusions and assumes unsafe 16-byte alignment for some views. The proposed address table retains slot IDs and liveness metadata, routes inactive writes to scratch and selects the new ABI mode explicitly. Audit pointer bounds/alignment and alias semantics before execution; do not assume it will be faster.

A separate full-capture audit finds all 193 norm gamma ranges immutable. Readonly gamma views are another possible compiler-scheduling experiment, not a measured gain. Tile-level scheduling research is summarized in ../../research.md.

Only one private GPU runner at a time: the competing-job watcher excludes this directory and cannot detect overlapping private runs.


October22 follow-ups: readonly gamma is numerically exact but no throughput gain (-0.041% ABBA). Selective small-task spread also passes but loses1.96%. Physical-slot addresses now have an isolated lifetime invalidation repair: a descriptor-only audit reproduced reused VkBuffer handles changing BDA, and the repaired raw-address host completes the former failing repeated benchmark. It is still9.54% slower, so none replaces this reference. A descriptor-retention-probe removal candidate reduces scalar spills42->24 and passes all9/65-frame checks; timing is pending. See ../no-descriptor-probes-evidence.json.
