# RDNA4 fork review — 2026-10-23

Primary repository https://github.com/MrLordCat/llama.cpp-rdna-lab ; inspected commit e648079e8656 (raw API evidence head-change.json; D138.md is pinned to that revision). This is a separate HIP/Vulkan dual-9070XT workload; its reported speedups are not evidence for our Q8 Vulkan mega shader. No repository code executed or installed.

The change packs grouped query heads into FA matrix columns for native FP8 decode. Our current op22 already has gqa_ratio mapping, grouped query strides and gqaStore, so the basic redundancy removal is already present. Native FP8 would change current Q8 KV arithmetic/quantization; no bit-exact shortcut inferred.

The report suggests hiding V operand-delivery latency through next-tile prefetch. Current shader stages V, waits, then runs PV WMMA, repeating four HSV tiles. A private fixed-shape prototype holds next-tile dequantized vectors in invocation registers while current tile is processed. This preserves current FP16 dequantization and PV arithmetic/barriers but raises live-register pressure; resource qualification and generated-code inspection must precede any performance claim. This is an independent shader experiment, not adoption of their HIP code.

The fork also records rejected MMVQ K-window and row geometry changes and corrections to naive bytes/token accounting. Our own integer one-row longer comparison was negative/inconclusive, so it is not promoted. Their MTP gains concern fewer model work units per accepted token, requiring acceptance and quality measurements; they do not establish a faster single-token mega kernel.
