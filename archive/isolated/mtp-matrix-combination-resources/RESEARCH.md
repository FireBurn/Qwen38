# Compiler research checked during audit

Primary LLVM source (web search2026-10-26): https://github.com/llvm/llvm-project/blob/main/llvm/lib/Target/AMDGPU/GCNSchedStrategy.cpp . Contains occupancy-versus-latency scheduling bias, occupancy relaxation and pressure/rescheduling controls. These are LLVM backend controls, not switches for our RADV/ACO pipeline. A useful comparison for a targeted ACO heuristic, not a drop-in patch or measured R9700 improvement.

https://github.com/llvm/llvm-project/blob/main/llvm/lib/Target/AMDGPU/AMDGPUTargetMachine.cpp exposes scheduler strategy selection and diagnoses coexec as gfx1250/gfx950-only. Do not recommend coexec for gfx1201.

No matching Mesa PR was established by the search; no claim that a relevant fix is absent upstream. No driver source edits or external actions this batch.
