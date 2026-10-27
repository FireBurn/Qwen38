# Current experimental full-FA reference

Shader: `../mk/gen/full256_fa_phase_bf16_pair.comp`, with its `.spv` and `.ops`. Host: `../bf16-pair/bin/libggml-vulkan.so.0.24.0`. Evidence and hashes: `../bf16-pair/verified-manifest.json`. Previous reference: NO_PROBE_REFERENCE.md.

Use 256 physical threads and 192 workgroups. Set GGML_VK_MEGA to the absolute shader .comp path and GGML_VK_MEGA_WGS=192. Enable each flag below with value 1:

- GGML_VK_MEGA_SHARED_LAYOUT
- GGML_VK_MEGA_SEGMENT_COUNTERS
- GGML_VK_MEGA_FUSE_NORM_QUANT
- GGML_VK_MEGA_NQ_PRESERVE
- GGML_VK_MEGA_FUSE_NORM_SCALE
- GGML_VK_MEGA_FUSE_GDN_GATES
- GGML_VK_MEGA_FUSE_BF16_PAIR

LD_LIBRARY_PATH selects the host above, then isolated/build/bin. Use native Vulkan/libc++ and preserve the R9700 visibility/queue/suballocation settings from checked runners. The shader has a #bf16_pair 1 header; the new host also needs the opt-in flag. Control shaders without the header cannot enable pairing accidentally.

## Evidence

- Previous safe LS32 mapping, shared typed binding, 149 removed retention checks, full cooperative-matrix FA phase reuse, and verified fusions remain.
- The new pass combines two small BF16 projections and the first projection's bias add. Outputs reuse the original buffer at different times; guarded retargeting preserves all live values. Two independent RMS records between the projections are retained.
- Both nine-frame and both 65-frame prompts match the native-subgroup control exactly.
- An additional 128 actual technical-document continuation tokens have byte-identical logits and conditional likelihood to the previous mega reference. Both differ slightly from stock; this is not corpus PPL or quality-equivalence proof.
- Separate coverage: 70 graphs; last 32 decode graphs have zero native operations, including FA. Initial slot-learning fallbacks remain.
- Actual allocation: 96 VGPRs, zero VGPR spills, 24 spilled SGPRs, 16 KB LDS, 241132 bytes code.
- Paired depth4096 n96/r3: 29.263201 vs29.115532 (+0.5072%). Longer n256/r4: 29.258012 vs28.928234 (+1.13999%). Paired gains over the preceding reference; absolute speeds from other batches are not directly comparable.

Still not faster than stock. Nothing installed or changed in Claude's trees. Frozen ABI0.24 Qwen3.8-27B/Q8KV/4K experiment; current-production qualification, corpus likelihood, rollback, speculative batches and other shapes remain outstanding. Only one private GPU runner at a time. No GPU runner remains active.

## Negative results and next work

Readonly gamma and selective small-task spreading have no gain. Raw-address slots now have a lifetime repair but are 9.54% slower. Do not substitute those candidates. Further directions include pairing the independent RMS records, extending the BF16 epilogue to its later decay gate only after liveness/stride proof, and establishing a fresh current-production baseline.


## Refreshed comparison

An interleaved full batch against privately copied current prodtree native binaries gives31.750868 native vs29.237272 mega:7.9166% slower, requiring8.5972% more throughput. Different core/ggml ABIs mean this is an end-to-end comparison. The copied development build and installed package are distinct artifacts; no installed-package timing claim is made here. Full paths/hashes and matching-input natural continuation results are in ../production-baseline-aa8/manifest.json. The independent RMS/projection bundle proposal is ../rms-pair/BUNDLE-PLAN.md; it is not yet implemented.


BF16/RMS overlap follow-up is not adopted. Shared dispatch passes model checks but longer paired timing is+0.007%, while direct-wave mapping is+0.021% in its short batch. Keep this BF16-pair shader/host; see ../bf16-rms-bundle/evidence.json.


Actual timing-shape coverage is now available: ../diagnostic-bf16-pair-4k-coverage/coverage.json traces depth4096,n256/r1.255/256decode graphs fully in mega; only decode0 learns new slots, and last32graphs have zero native operations includingFA. IO-instrumented throughput is excluded. CPU metadata caching reduces profiled fusion cost but has no demonstrated unprofiled throughput gain, so host remains bf16-pair.


Flat matvec grid shortcuts pass numerical checks but show no gain, with or without explicit branch retention. They are not adopted. Next resource-pressure experiment is ../GDN-LDS-PLAN.md; no physical-grid increase is qualified by that plan.
