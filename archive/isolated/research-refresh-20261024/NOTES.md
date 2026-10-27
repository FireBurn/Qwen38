# Source refresh, 24 October 2026

Primary source: https://github.com/ggml-org/llama.cpp/pull/30517

API metadata and file patches archived read-only. PR30517 merged17October2026; head6e9b69aa9e02709cf9469adffcc5f14ccde395ba. Changed CUDA/HIP MMVQ and vecdotq only. No external source executed and no public contribution made.

Mechanisms: process two packed words per partial dot instead of one; integer correction for Q3/Q6 bias instead of per-byte subtract; some type/device-specific row/warp geometry changes. Reports include R9700 operator results and smaller-model end-to-end results. They are hypotheses for this machine, not our measurements. Current Vulkan Q3 already computes 16 values per partial dot, so a literal VDR1-to2 port is not applicable. Current Q6 uses float activations; switching it to Q8 integer arithmetic would add activation quantization and require a quality gate. That is distinct from our exact Q6 scale handoff candidates.

Private derived experiment q3-shared-bias removes Q3 packed byte recentering and computes -4*sum(16 signed activation bytes) once per existing two-row cohort. Each row's integer dot starts with that correction. Integer distributivity plus bounded accumulators preserves exactly the original integer result and float arithmetic. This shares the correction across rows instead of blindly copying the upstream per-word pair of dots. CPU identity and SPIR-V validation are prerequisites; current-machine GPU correctness, allocation and timing remain required.
