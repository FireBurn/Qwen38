# Native fusion metadata-node expansion


## Expanded coverage across metadata nodes

The native planner now has an opt-in extension that crosses at most eight graph nodes, accepting only VIEW, RESHAPE, PERMUTE, TRANSPOSE or NONE while still requiring the matrix consumer to read the original SwiGLU tensor directly. It stops at an executable operation. Input tensors are explicitly required to be F32; existing shape, contiguity, Vulkan-buffer and alias guards remain.

The captured model increases from **14 to 56 fused target pairs per graph**, while retaining one draft pair. Both 16- and 136-workgroup tests pass the complete canonical byte audit, including bounded-head variants. Each enabled model arm executes 1159 fused pairs across 20 target and 39 draft graphs. The additional target pairs cross a single metadata node; they do not introduce dependencies across unrelated dispatches.

A focused operator test explicitly inserts a view between each SwiGLU and its direct matrix consumer. Native/fused C1 and C2 outputs remain byte-identical across all 64 pairs and four patterns. The GPU pipeline remains 48 VGPRs, zero LDS/scratch/spills, 820 bytes. [Operator evidence](operator-views16/checks.json), [coverage counts](views-coverage.json), [16-workgroup model comparison](model-views16/comparison.json), [136-workgroup comparison](model-views136/comparison.json).

This expands opportunities; it does not establish a speed gain. A 512-token off/adjacent/expanded forward/reverse comparison is prepared with identical backend, core, driver, copy override and bounded-head settings. It has not started. The standalone timing job remains live, waiting for its original CPU/build quiet gates. Current production and long-context comparisons remain pending.
