# Source refresh, 2026-10-23

Primary sources captured read-only with GitHub API metadata. External reports are hypotheses, not measurements on this machine.

- stew675/llama-cpp-rdna-boosts tree 374c91a5055a083a69161a884fe354c73e12c465. PR195 fetch-ahead preserves packed Q8 K/V in registers, delays conversion, and uses local-only barriers to avoid draining future global loads. Reports concern its HIP band kernel and contexts up to110K. Current private FA has Bc64/HSK256, per-16-column K staging and local workgroup barriers. A smaller next-K-slice pipeline is now isolated/fa-k-slice-prefetch; do not transfer their full-model speed figures.
- ROCm/llvm-project PR3014 adds a Clang s_prefetch_inst builtin, closed without merging (API merged=false). Local clang23 gfx1201 __has_builtin reports instruction-prefetch unavailable; data-prefetch and sudot8 available. This does not establish that LLVM's underlying intrinsic/assembler is absent. A Vulkan shader uses ACO, so swapping the host Clang cannot enable this instruction in the mega shader.
- Matching ACO source defines s_prefetch_inst and s_prefetch_inst_pc_rel but search finds no emission use. The existing loop prefetch-mode adjustment in aco_assembler.cpp is explicitly capped at GFX11. RADV does set an entry instruction-prefetch size. Selective future operator-code prefetch is a distinct possible private compiler experiment, needing actual PC-relative range/fixup validation and ISA evidence before GPU tests; not implemented.
- llvm/llvm-project PR140674 is open, allowing memory clustering across different base pointers in LLVM MISched. Its Babelstream claim does not transfer to ACO. ACO already has separate hard-clause formation and memory scheduler machinery; a port would need to identify an actual missed load-clustering opportunity first.
- ggml-org/llama.cpp PR27952 merged2026-09-24, integer cooperative-matrix matmul. Wave32, quantized multi-row matmul/prefill is a separate workload from the current single-token wave64 GEMV mega. Not a new drop-in decode patch. Existing native base must include relevant current upstream paths before comparison.

Sources:
https://github.com/stew675/llama-cpp-rdna-boosts
https://github.com/ROCm/llvm-project/pull/3014
https://github.com/llvm/llvm-project/pull/140674
https://github.com/ggml-org/llama.cpp/pull/27952
