# Current experimental full-FA reference

Shader: `../mk/gen/full256_fa_phase_bounds.comp`, with `.comp.spv` and `.comp.ops`.
Host: `../gdn-gather-one-row/bin/libggml-vulkan.so.0.24.0`.
Manifest: `../gdn-gather-one-row/verified-manifest.json`.
Previous reference: `BOUNDS_REFERENCE.md` (and preceding `BF16_PAIR_REFERENCE.md`).

Use 256 physical threads, native 64-lane subgroups and 192 workgroups. Set `GGML_VK_MEGA` to the absolute shader `.comp` path and `GGML_VK_MEGA_WGS=192`. Enable each flag with value 1:

- `GGML_VK_MEGA_SHARED_LAYOUT`
- `GGML_VK_MEGA_SEGMENT_COUNTERS`
- `GGML_VK_MEGA_FUSE_NORM_QUANT`
- `GGML_VK_MEGA_NQ_PRESERVE`
- `GGML_VK_MEGA_FUSE_NORM_SCALE`
- `GGML_VK_MEGA_FUSE_GDN_GATES`
- `GGML_VK_MEGA_FUSE_BF16_PAIR`
- `GGML_VK_MEGA_GATHER_ONE_ROW`

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

## One-row initial recurrent-state gather bypass

Host-only change; bounds shader/SPIR-V is unchanged. For exactly one cache row, zero is the only legal GET_ROWS index. Logical consumer proof requires one GDN state reader, no exported gathered state, exact contiguous3MiB cache/state, one-token/sequence/K1 and transient COMPUTE output. Runtime exact-PC, same-flush and intervening full-range guards then retarget the GDN initial-state descriptor and remove GET_ROWS. No delayed row-index read; original packed state output/copy preserved. Every rejected shape retains generic behavior.

Both9/65prompts exact. Positive/negative CPU proof witness passes. Natural128 full-logit SHA remains6bc08dae224be6b82c2ca594004596dd8a3e6f587a950137fc535786c4a37900. Actual4K n256coverage:255/256fullyMega, last32zero nativeops/FA and44gathers removed per token. Runtime maps confirm private host library. Shader resource allocation unchanged96VGPR/24SGPRspills/16KB.

Same-host on/off alternating4K n96/r3:29.3390375→29.5945165tok/s(+0.8708%). Fuller4K n256/r4:29.2912575→29.5843385(+1.0006%). This qualifies the new private reference; it is not a fresh native-vs-mega victory. Current-production port and broader/speculative quality scope remain unqualified. All GPU jobs terminal at promotion.
