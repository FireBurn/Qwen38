# Flash Attention scratch lifetime experiment

## Evidence

- Corrected full shader: 192 VGPRs, 30,720 bytes LDS; native-subgroup variant: 192 VGPRs, 28,672 bytes LDS.
- Removing FA produces a 96-VGPR / 4,096-byte remainder.
- ACO records 87 pre-scheduling VGPRs for the full shader. Disabling scheduling does not lower allocation. Therefore 192 should not be treated as an established unavoidable arithmetic requirement.
- Mesa `aco_live_var_analysis.cpp` limits resident workgroups using `lds_limit / lds_per_workgroup`; its register-allocation budget depends on the resulting wave count. Reducing LDS may change the register budget as well as the shared-memory limit. This is a hypothesis to test, not a demonstrated throughput result.
- Vulkaninfo on the R9700 reports VK_KHR_workgroup_memory_explicit_layout plus workgroupMemoryExplicitLayout, ScalarBlockLayout, 8BitAccess and 16BitAccess true. The current isolated host does not enable this extension/feature.
- `alias_probe.comp` compiles and passes Vulkan 1.2 SPIR-V validation. Its disassembly has WorkgroupMemoryExplicitLayoutKHR, WorkgroupMemoryExplicitLayout16BitAccessKHR and Aliased on both typed blocks. The initial syntax-only probe was not GPU-tested; see the separate runtime probe below.

Primary spec: https://docs.vulkan.org/refpages/latest/refpages/source/VK_KHR_workgroup_memory_explicit_layout.html . This explicitly permits aliasing scratch data with non-overlapping lifetimes. GLSL syntax: https://github.khronos.org/Vulkan-Site/glslext/latest/glslext/ext/GL_EXT_shared_memory_block.html .

## Candidate layout to audit before implementation

The current per-type shared packer cannot exploit every phase or overlap different typed arenas. For the captured FA shape (Br16, Bc64, HSK/HSV256, WG256, Q8 K/V), consider:

| Scratch region | Candidate offset | Size | Phases |
| --- | ---: | ---: | --- |
| Q / V staging | 0 | 8,448 bytes | Q during QK; V during PV |
| K staging / float scores / output tile | 8,448 | 4,096 bytes | K during QK; scores during softmax; output during PV |
| Half probabilities | 12,544 | 3,072 bytes | After softmax through PV |
| Float slopes | 15,616 | 64 bytes | FA lifetime |

Candidate end: 15,680 bytes, potentially 16 KB after hardware allocation rounding. This is arithmetic on source array sizes, not a verified allocation. Other operations' scratch can share this storage only if the entire cross-type overlap/lifetime audit proves it safe.

Required changes and checks:

1. Enable the advertised extension and 16-bit explicit-layout feature in a separate opt-in host library; validate the probe's output (expected 0x3c003c40) and reported LDS allocation before editing FA.
2. Establish equivalent explicit typed layouts without phase reuse first, preserving results.
3. Separate K and V staging offsets even though the current source uses one array for both.
4. Q currently persists across the KV loop. Reload Q at the start of each KV tile (or retain its values in registers) before reusing its storage for V. Loading Q again must preserve the exact scaling/conversion order.
5. Add a uniform workgroup barrier after the final QK matrix use and before overwriting K staging with float scores. Audit every existing barrier at softmax/PV transitions and at the next KV iteration.
6. Prove that score storage is dead before reusing it for output tiles. Keep probabilities and V staging disjoint during matrix multiplication.
7. Put other operations' float scratch at the same physical base only when FA is not active; FA's persistent float slopes need their dedicated offset. Do not simply overlap all current arrays at offset zero.
8. Validate SPIR-V, real driver LDS/VGPR allocation, forced logits, longer state evolution and FA contexts. Only then evaluate greater physical workgroup counts using the measured resident-group bound; a persistent grid barrier can deadlock if the grid exceeds residency.

No speedup is assumed: Q reloads and extra barriers have a cost. A smaller allocation must be measured together with actual occupancy, workload distribution and model throughput. Keep FA within the same kernel throughout this experiment.

## Runtime feature probe completed

`prepare_host.py` builds a separate library in `host/`, enabling the extension and its 16-bit feature only with `GGML_VK_MEGA_SHARED_LAYOUT=1`. `run_probe.py` runs the dedicated one-op synthetic graph on R9700, rejecting CPU fallback. The module uses 128 threads: wave 1 writes a word in a float view, and wave 0 reads its two half components through an explicitly aliased block after a barrier. The observed packed output is 0x3c003c40, matching input word 64. Trials 1 through 3 match; the first graph warms descriptor slots through native fallback.

The compiler initially removed a constant/same-thread probe's shared storage entirely. That was replaced by this input-dependent cross-wave version, whose driver statistics report 1,024 bytes LDS and whose output verifies the actual typed alias. The runner asserts nonzero LDS allocation to prevent an optimized-away test from passing as a hardware shared-memory test. `probe-result.json` and `probe.log` hold the results.

This verifies feature enabling and the alias mechanism. It does not yet validate the proposed full FA phase layout or its model performance.

## Full phase reuse validated

The full cooperative-matrix FA phase layout builds and validates. Driver allocation is 96 VGPRs (zero VGPR spills), 108 SGPRs (40 spilled), 16,384 bytes LDS, 227,188 bytes code. Both nine-frame checks and both 65-frame forced-token regressions are bit-identical to the native-subgroup control. See validation/fa-phase-results.json and fa-phase-stress-results.json. This preserves relative arithmetic/state evolution, not stock PPL or speculative rollback qualification.

The measured resources support a conservative 192-workgroup follow-up: Mesa ac_gpu_info.c gives GFX12 768 wave64 VGPRs per SIMD and four SIMDs per WGP, so 96 VGPRs permits eight waves/SIMD. Four waves per 256-thread group permits eight groups/WGP. LDS is 128 KB/WGP / 16 KB/group = eight groups. Across 32 WGP the resource bound is 256 groups; 192 reserves 25% headroom. SGPR allocation is fixed 108 per wave with 16-wave capacity, and multi-wave group hardware cap is 32/WGP. This is a resource calculation, not a portability guarantee; keep other grids unchanged and validate 192 separately. Do not reuse Claude's unsafe 512-thread/192-VGPR grid assumptions.
