# Identical typed descriptor arrays

`vk_mega_apply_pending` builds the same VkDescriptorBufferInfo for every typed view and writes it to all 42 array bindings. The slot key contains only buffer/offset/range, not the view type. Native shaders already put typed aliases on the same binding: Q6 A/A_PACKED16 use binding 0, while float/vec2/vec4 activation views all use binding 1.

`build_shared_binding.py` retains every typed GLSL block and its memory qualifiers, but remaps all typed views and PFV to binding 1. Tape stays at binding 0. All descriptor variables retain Aliased before SPIR-V optimization. The .ops header becomes #views 1 2048, so the unmodified host builds one 2048-entry typed descriptor array and updates it once per slot. No new API features, model conversion or host ABI changes are needed. The source derives from the corrected LS32 safe-slots reference.

Both nine-frame checks pass bit-identically. Driver resource allocation remains 96 VGPRs / 16 KB LDS, 42 spilled SGPRs, zero VGPR spills; code drops from 237288 to 235948 bytes. Longer checks and throughput measurement remain required. No CPU/GPU speedup is assumed from fewer descriptor copies alone: earlier numeric-slot lookup changes were hidden by GPU work.

## Longer results

Both 65-frame regressions pass bit-identically. A separate long-prompt native-dispatch trace confirms 62 of 64 decode graphs entirely use the mega shader. The first graph learns slot mappings and one later graph has native FA while a new KV range is learned; the last 32 graphs have no native operations.

4K-depth n256/r4 ABBA: shared 29.104420 versus control 28.758740 (+1.202%). A quiet repeat gives 29.113776 versus 28.795235 (+1.106%). The initial batch followed higher historical system load; the repeat began without active compilers, with one-minute load around 0.5. Stock anchors in the initial batch are 31.936948/31.726929. This is a measured incremental gain, still slower than base. GPU resource maxima remain unchanged, so lower SGPR allocation is not claimed as the cause. Source/header/host hashes are recorded in shared-binding-verified-manifest.json.
