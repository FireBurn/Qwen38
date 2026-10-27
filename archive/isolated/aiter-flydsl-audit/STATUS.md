# User-linked AITER/FlyDSL lead

Exact post2113992350489788573 retrieved through X syndication endpoint; created2026-10-24T13:53:47Z. It credits MI355X MiniMax M3.1 performance to AITER FlyDSL fused MoE and other fused kernels. Earlier web search returned unrelated megakernel posts; those are not the linked post.

Primary source leads: https://github.com/ROCm/aiter , https://rocm.docs.amd.com/projects/FlyDSL/en/latest/installation.html , https://github.com/ROCm/FlyDSL/blob/main/kernels/gemm/rdna_f16_gemm.py . Current AITER README labels gfx1201 experimental. FlyDSL documentation distinguishes architecture support from actual kernel/dtype/shape validation. MI355X CDNA4 MFMA schedules cannot be directly transplanted into R9700 RDNA4 WMMA or Vulkan/ACO.

Retrieved RDNA kernel is wave32, 128x128x32 tile,128threads, ping-pong LDS, split global-to-register and register-to-LDS moves, K padding,128bit copies, gfx120x v8 WMMA ABI. It is a dense BF16/F16 GEMM reference, not a drop-in quantized GGUF GEMV. Proposed application: inspect ISA and register/latency scheduling for a future RDNA wave32 FA branch and larger token-batch GEMM; compare producer-consumer fused activation/quantization with already tested private GLU/SiLU variants. No performance claim, no installation, no GPU run, no external repository edits. Our current wave64 mega cannot merely insert wave32 fragments.

Prioritize closing the newly reproduced two-query attention fallback/numerical contract gap before porting more numerical changes. Preserve this as a separate backend research track. Search result claiming issue6596 was RDNA KDA is incorrect: opening primary GitHub shows a tolerance-cleanup issue, so that search snippet is not evidence.
