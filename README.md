# Qwen38: AMD inference optimization experiments

Research notes and evidence from attempts to accelerate Qwen3.8 inference on an **AMD Radeon AI Pro R9700**, principally llama.cpp's Vulkan backend and a persistent mega kernel containing matrix operations, recurrent operations and Flash Attention.

**No faster-than-native mega kernel has been established.** Several changes improve individual components or the previous mega kernel. That is a different result from beating the current native backend.

## Start here

- [Results and conclusions](docs/RESULTS.md): measured gains, losses and inconclusive results.
- [Experiment catalog](docs/EXPERIMENTS.md): the main lines of investigation.
- [Smaller fusions and shader roadmap](docs/ROADMAP.md): what the evidence suggests trying next.
- [Native fusion rounding diagnosis and corrected audit](docs/NATIVE-FUSION.md).
- [Shuffle8variant, source and model checks](docs/SHUFFLE8.md).
- [Native quantizer shuffle checks](docs/NATIVE-QUANT-SHUFFLE.md).
- [Measurement and reproduction requirements](docs/METHODOLOGY.md).
- [Transfer-copy correctness investigation](docs/COPY-BUG.md).
- [SDMA transfer-queue alternative and checks](docs/SDMA.md).
- [Research and upstream references](docs/REFERENCES.md).
- [Complete exported report index](docs/ARCHIVE-INDEX.md) and [machine-readable manifest](manifest.json).

The archive preserves historical reports, including failed experiments and subsequently superseded interpretations. **A report saying “queued” or “pending” is historical state, not proof that the test later passed.** Use the current summaries and linked result artifacts to interpret it. Timings marked under load, unstable, partial, or invalid must not be promoted to confirmed speedups.

## Main findings

1. Reducing launches alone was insufficient. A single-submit implementation removed 19 segments but ran slower than the segmented kernel.
2. Register and shared-memory reductions made the combined kernel substantially smaller, but did not close the native matrix-performance gap.
3. Cache-warm attention microbenchmarks and small fusion microbenchmarks can improve without improving token throughput.
4. Matrix/weight-stream work dominates much of this dense model. Smaller native-path fusions and focused shader changes are credible next experiments, but their expected end-to-end effects must be measured.
5. A reproducible four-dword RADV compute-copy failure invalidated some small-shape comparisons. One/two-dword compute copies and CP DMA passed the captured reproducer. This is a scoped observation, not a claim that all RADV copies are broken.

## Scope of this repository

This is an **evidence archive and research plan**, not a ready-to-install inference engine or a distribution of model weights. It includes reports, compact JSON results and a small MIT-licensed experimental shader, not raw conversation transcripts, model files, GPU binaries, shader caches, complete third-party source trees, or production launchers. Paths identifying the private workspace have been replaced with placeholders. Some historical references point to artifacts that are not exported; the manifest explicitly records what is present.

Experiments span different llama.cpp revisions, backend ABIs, prompts, speculative settings, context lengths and driver snapshots. Results from different stacks are not interchangeable. In particular, the private `.24` backend is not the newer production `.27` baseline.

Documentation and analysis were developed with AI assistance and reviewed against local artifacts. Negative results are intentional: this record should help avoid repeating work that already failed.
