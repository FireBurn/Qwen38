# R9700 runtime/compiler research

## Queue-wait pathology: concrete hardware-matching upstream evidence

https://github.com/ROCm/TheRock/issues/9297 (redirect of legacy-rocm-build6685)
https://github.com/vllm-project/vllm/issues/58639

Reporter uses R9700/gfx1201 and a small standalone HIP reproducer: two waiting streams increase tiny-kernel latency substantially, while a large memory read changes little. Workloads, runtime and queue configuration matter. These are reporter observations, not local reproduction. No ROCm environment or kernel/firmware setting changed here.

Current private backend is Vulkan/RADV/ACO, not HIP/HSA. q8-two-column-f32/ggml-vulkan.cpp6965..6971 selects compute and transfer families and sets single_queue only when same family has exactly one queue.7183..7190 creates two family queues, two queues in one family, or one queue depending on capabilities. GGML_VK_ALLOW_GRAPHICS_QUEUE permits graphics; it does not force single_queue. Therefore neither claim of identical HIP pathology nor claim of a guaranteed single queue is justified. A future isolated Vulkan comparison should instrument selected families and actual pending semaphore waits, preserve uploads outside timed phases, and compare same workload with one queue versus current selection. Do not apply GPU_MAX_HW_QUEUES as a Vulkan optimization without evidence; it controls a different runtime.

## AOTriton0.14.2b / FlyDSL

https://github.com/ROCm/aotriton/releases/tag/0.14.2b
Official release provides flyc attention for gfx1201 as well as gfx950 and updates tuning. Its release also documents scaling-factor precision fixes. This is useful source/reference material for attention layout/scheduling, not a binary replacement for our quantized KV persistent Vulkan shader. Changes that move scaling across half conversion require explicit numerical qualification. No reported release speed ratio is a local model-speed result.

## LLVM boundary

backend-dependency-audit.json confirms private driver configured llvm=disabled and amd-use-llvm=false; GPU shaders use ACO. LLVM backend or AMD fork changes need an applicable algorithm/codegen idea ported to ACO, a shared host-component impact, or an explicitly separate HIP experiment. Swapping LLVM builds is not a demonstrated direct shader fix here.
