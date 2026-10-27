# Dynamic VGPR research cross-check (2026-10-26)

AMD RDNA4 ISA section3.3.3 explicitly restricts dynamic VGPR allocation to wave32, requires launch mode, and reserves a CU/WGP for dynamic-enabled workgroups. Current unified shader is wave64. No drop-in switch or benefit established.
https://www.amd.com/content/dam/amd/en/documents/radeon-tech-docs/instruction-set-architectures/rdna4-instruction-set-architecture.pdf

LLVM primary docs describe amdgpu-dynamic-vgpr-block-size0/16/32 and matching callee requirements; chained functions encode dynamic resource blocks in _dvgpr$ symbols. This is a useful architectural lead for independently compiled operator continuations, not supported evidence for current Vulkan compute path.
https://llvm.googlesource.com/llvm-project/+/b02b395a1e75030708efc099f449f96436a90141/llvm/docs/AMDGPUUsage.rst

AMD ROCm ABI documentation table for compute_pgm_rsrc3 distinguishes gfx120* reserved dynamic-VGPR bit from gfx125* enabled bit. Therefore even a wave32 rewrite needs exact gfx1201 driver/launch-mode support confirmed; ISA chapter alone is insufficient.
https://rocm.docs.amd.com/projects/llvm-project/en/docs-7.14.1/LLVM/llvm/html/AMDGPUUsage.html

Reviewed amd-gfx patch posting, not a confirmed merged fix: Siwei He,2026-08-14,drm/amdkfd dynamicVGPR save/restore trap handling. Scope is KFD context save, not current RADV shader scheduling or a measured throughput improvement. No kernel changes warranted by this evidence.
https://www.mail-archive.com/amd-gfx%40lists.freedesktop.org/msg148950.html

Inference: a hypothetical dynamically resizing persistent interpreter also needs its global barrier forward-progress proof redone. Launching more waves on minimum resource demand does not establish that every wave can later obtain its peak register demand without waiting on waves blocked at a grid barrier. No such implementation or proof exists here.
