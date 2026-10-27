# Current experimental full-FA reference

Shader: `../mk/gen/full256_fa_phase_bounds.comp`, with `.comp.spv` and `.comp.ops`.
Host: `../bf16-pair/bin/libggml-vulkan.so.0.24.0`.
Manifest: `../bounds/verified-manifest.json`.
Previous reference: `BF16_PAIR_REFERENCE.md`.

Use 256 physical threads, native 64-lane subgroups and 192 workgroups. Set `GGML_VK_MEGA` to the absolute shader `.comp` path and `GGML_VK_MEGA_WGS=192`. Enable each flag with value 1:

- `GGML_VK_MEGA_SHARED_LAYOUT`
- `GGML_VK_MEGA_SEGMENT_COUNTERS`
- `GGML_VK_MEGA_FUSE_NORM_QUANT`
- `GGML_VK_MEGA_NQ_PRESERVE`
- `GGML_VK_MEGA_FUSE_NORM_SCALE`
- `GGML_VK_MEGA_FUSE_GDN_GATES`
- `GGML_VK_MEGA_FUSE_BF16_PAIR`

Select the host directory above, followed by `isolated/build/bin`, in `LD_LIBRARY_PATH`. Retain the native Vulkan/libc++ R9700 settings from the checked runners. No installed packages, Claude files or launchers changed.

## Scratch bounds correction

The previous slope array declared 16 floats, but the cross-subgroup masked-tile reduction addresses entries 16–19. The new declaration covers all 20 entries; IQ storage moves from byte 15680 to 15712, disjoint from them. Allocated LDS remains 16 KB.

The installed driver's final lowered instruction listing is byte-identical to the preceding reference. No throughput gain is claimed for this correction.

## Verification

- Both nine-frame and both 65-frame prompts match the preceding controls exactly.
- Full logits on 128 actual technical-document continuation tokens match the previous mega reference. Conditional PPL 5.308676045090262 is inherited and differs from native; this is not a corpus quality-equivalence claim.
- An odd-row Q5_K/Q3_K/Q4_K witness passes 16 graphs with changing inputs against native. Its final eight graphs run entirely in mega.
- Actual depth-4096, n256/r1 coverage: 255/256 decode graphs entirely in mega; the final 32 have zero native operations, including FA. Trace throughput is excluded.
- Resources: 96 VGPRs, 24 spilled SGPRs, zero VGPR spills, 16 KB LDS, code 241132 bytes.

## Performance status and rejected experiments

Still no faster-than-base result. The earlier current-development native-vs-mega snapshot was 31.750868 versus 29.237272 tok/s, 7.9166% behind, across different core ABIs. This bounds correction changes no lowered instructions and is not a fresh production benchmark.

Full accumulator initialization removes six values carried across the record loop. With rolled FA, actual post-spill demand falls from 92 to 79; final allocation remains 96. Its longer 192-group comparison is −0.0483%, so it is not adopted. The 224-group grid passes numerical qualification with documented resource headroom but has no sustained gain established; reference stays at 192.

Scalar row indices and a 12 KB layout reduce pre-allocation demand further. Coarse `ACO_DEBUG=nosched` reaches 72 allocated VGPRs but is 10–15% slower in the microbenchmark. Do not enable it in the reference. See `../fa-scalar-rows/PLAN-12K.md`, `../nosched-12k/RESIDENCY.md`, and `../grid224/RESIDENCY.md`.

Current-production port, broader likelihood and long-context quality, rollback/speculative batches and other shapes remain outstanding. Keep the overall optimization goal active.
