# Research and upstream references

These are mechanisms and design references, not measured speedups on this R9700 unless a local experiment explicitly says so. Historical source checks and downloaded patch snapshots are described in the [research notebook](../archive/research.md).

| Primary source | Potential use | Applicability limit |
|---|---|---|
| [AMD R9700 specifications](https://www.amd.com/en/products/graphics/workstations/radeon-ai-pro/ai-9000-series/amd-radeon-ai-pro-r9700.html) | Hardware constraints and advertised bandwidth | Peak bandwidth is not measured achieved DRAM traffic |
| [AMD RDNA4 ISA](https://docs.amd.com/api/khub/documents/uQpkEvk3pv~kfAb2x~j4uw/content) | Instructions, wave constraints and synchronization | New instructions require compiler exposure and workload validation |
| [Cohere mega kernel](https://github.com/cohere-ai/cohere-megakernel) | Tile dependencies and resident task scheduling | NVIDIA/other model results are not Vulkan portability evidence |
| [Mirage](https://github.com/mirage-project/mirage) / [MPK paper](https://arxiv.org/abs/2512.22219) | Compile model DAGs into persistent tasks | CUDA-oriented, not a drop-in backend |
| [Flash Linear Attention](https://github.com/fla-org/flash-linear-attention) | GDN preparation and recurrent fusion | Must match Qwen state layout, rounding and rollback |
| [FlashInfer attention states](https://docs.flashinfer.ai/tutorials/recursive_attention.html) | Chunked attention and composable states | Partial states are query-specific |
| [llama.cpp PR 31197](https://github.com/ggml-org/llama.cpp/pull/31197) | Row-major probability layout / fragment reuse | Local variants were qualified independently; local timing must decide |
| [llama.cpp PR 31196](https://github.com/ggml-org/llama.cpp/pull/31196) | Wider-column AMD Q8 matvec | Wider batches are not the captured C1/C2 workload |
| [R9700 experiment discussion](https://github.com/ggml-org/llama.cpp/discussions/21043) | Row packing and driver comparison leads | Different model/revision/OS; author-reported results, not local evidence |
| [LLVM memory-clustering proposal 140674](https://github.com/llvm/llvm-project/pull/140674) | Memory scheduling ideas | ACO has different scheduling/aliasing constraints |
| [Mesa ACO function calls](https://docs.mesa3d.org/drivers/amd/function-calls.html) | Code-size/outlined-call research | Current compute lowering and barrier inlining are not a ready toggle |
| [RADV driver and copy-path options](https://docs.mesa3d.org/drivers/radv.html) | Private copy-path isolation | Overrides are experimental controls, not general performance recommendations |
| [AMDGPU user queues](https://docs.kernel.org/gpu/amdgpu/userq.html) | Lower submission overhead | Does not imply support in the inspected RADV path or lower shader work |
| [Vulkan device-generated commands](https://docs.vulkan.org/features/latest/features/proposals/VK_EXT_device_generated_commands.html) | Cached native-kernel command templates | Dependency barriers are still required; preprocessing also costs work |
| [AOTriton 0.14.2b](https://github.com/ROCm/aotriton/releases/tag/0.14.2b) | gfx1201 attention scheduling/reference implementations | Not a persistent Q8-KV Vulkan replacement |
| [T-MAC](https://github.com/microsoft/T-MAC) | Activation-dependent low-bit LUT methods | CPU/NPU-oriented; GGUF block scales and GPU register tables complicate reuse |

## Additional upstream notebooks

- [RDNA lab](https://github.com/MrLordCat/llama.cpp-rdna-lab): external D138 and performance reports are referenced rather than republished; the archive retains our local review.
- [RDNA fetch-ahead proposal](https://github.com/stew675/llama-cpp-rdna-boosts/pull/195): external patch documentation informed the independent K-slice experiment. Its complete upstream README is not republished.

## LLVM, ROCm and ACO

The tested Vulkan shaders are generated through **ACO**. LLVM/clang may build the host driver and application, while HIP/HSA experiments use a different GPU compiler path. A newer host clang, LTO setting or ROCm compiler fix does not automatically change ACO shader code.

Dynamic VGPR, wave32, instruction prefetch and bank-hint proposals were investigated. Compiler acceptance or an opcode definition was not treated as runtime support or a measured gain. The current wave64 kernel cannot simply be changed to wave32: subgroup counts, cooperative-matrix mapping, reductions and shared ownership must be redesigned and requalified.

No contribution was made to Mesa GitLab. The private experiments are not upstream patches or endorsements.

## Additional upstream leads checked October 27

- [CUDA MoE gate/up plus GLU MMQ, PR 31188](https://github.com/ggml-org/llama.cpp/pull/31188): extends dense fusion from PR 29948 to expert FFNs. Its published result concerns NVIDIA prompt processing, so it is design evidence rather than an R9700 dense C1/C2 decode result. Our older gate/up fusion did not establish a model gain.
- [RDNA4 Q3_K discussion 22663](https://github.com/ggml-org/llama.cpp/discussions/22663): reports a Q3 efficiency gap, principally on HIP, with a later Vulkan comparison. This supports investigating quant-specific loading and unpacking; it does not establish that this Vulkan build has the same bottleneck. The current model-weighted mix and captured native shaders remain the appropriate local tests.

### Additional primary sources checked 2026-10-28

- [llama.cpp OpenCL Q3_K support, PR31172](https://github.com/ggml-org/llama.cpp/pull/31172), merged October27, includes a [Q3 structure-of-arrays matrix-vector/tiled-matrix implementation](https://github.com/ggml-org/llama.cpp/commit/d04eb29e8b87328cfb4463bc75796a26e880b8e0). Its conversion/restore and separated quant/high-bit/scale streams offer concrete layout ideas. Portability or speed on this Vulkan/R9700 stack is untested; a small tiled layout could potentially preserve aligned word access without padding every block. That is a proposed experiment, not a result.
- [Vulkan MTP buffer-residency report, issue30688](https://github.com/ggml-org/llama.cpp/issues/30688), reports target compute buffers becoming nonresident near full VRAM on R9700. This is a user-reported different workload, not a diagnosis of these experiments. It motivates checking requested/resident VRAM when adding repacked copies, in addition to checking numerical equivalence and timestamps.
