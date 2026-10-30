# Qwen38: AMD inference optimization experiments

Research notes and evidence from attempts to accelerate Qwen3.8 inference on an **AMD Radeon AI Pro R9700**, principally llama.cpp's Vulkan backend and a persistent mega kernel containing matrix operations, recurrent operations and Flash Attention.

**Padded Q3 at the native submission cap100 independently confirms a +1.33% gain over stock native defaults**, descriptive95% interval[+0.35%,+2.32%], across11load-matched blocks in a fixed48-run confirmation. Discovery separately measured+1.86%. All96processes preserve exact tokens/counters, no new GPU errors; approximately3GiB extraVRAM. [Evidence, baseline correction and limits](docs/NATIVE-DEFAULT-BASELINE.md). **No faster-than-native mega kernel has been established.** The cap400 combination was slower than native-default stock, and older+8.43% gains used a constrained memory harness.


## Start here

- [Wider native argmax](docs/NATIVE-ARGMAX.md): fixed72modeldiscovery+1.92%overstock; independent48confirmationrunning, not yet confirmed.
- [Restricted target greedy sampling](docs/NATIVE-GREEDY-SAMPLING.md): allthree530rawrows/config exact, backend activity verified; fixed72test finds no gain overstock.
- [Current work and latest results](docs/CURRENT-STATUS.md): completed experiments, confirmed scope and untested next steps.

- [Direct native-default stock comparison](docs/NATIVE-DEFAULT-BASELINE.md): cap100Q3 independently confirms+1.33%; earlier cap400combination1.69% slower.
- [Mapped-VRAM path](docs/NATIVE-MAPPED-VRAM.md): restores an existing native default, removes2,442queuecalls; independent48-run confirmation+28.3% versus the old harness; native-default comparison now complete.
- [Immutable GPU rotation matrices](docs/NATIVE-CONSTANT-ROTATION.md): new private core cache passes530targetrows and repeated KV clears, eliminating444repeated uploads; no model speed claim yet.
- [Native transfer observer](docs/NATIVE-TRANSFER-OBSERVER.md): identifies1,850 synchronous tensor-set submissions per short decode; ownership-preserving batching is the next target.
- [Native submission budget](docs/NATIVE-SUBMIT-BUDGET.md): fewer batches and a small discovery gain; independent under-load confirmation remains unqualified.
- [Native fusion-plan cache](docs/NATIVE-FUSION-PLAN.md): exact cached CPU decisions and mutation tests; fixed under-load A/B establishes no incremental gain.
- [Results and conclusions](docs/RESULTS.md): measured gains, losses and inconclusive results.
- [36-run under-load A/B test](docs/UNDER-LOAD-AB.md): independent confirmation finds no measurable gain.
- [Bounded Q3 gate/up/SwiGLU fusion](docs/Q3-PAIR-GLU.md): exact fused operator with lower focused GPU time; full-model under-load A/B remains unqualified.
- [Q3 cross-column weight reuse](docs/Q3-COLUMN-REUSE.md): 24% fewer C2 instructions and exact model outputs, but no qualified model or C2 operator gain.
- [GDN reader-index follow-up](docs/GDN-READER-INDEX.md): exact outputs and lower CPU cost, but fixed under-load A/B finds no qualified token-rate gain.
- [Native command observer](docs/NATIVE-COMMAND-OBSERVER.md): exact native outputs and repeated recording arguments, including a KV transition; no replay or new speed claim.
- [Submission-only contribution experiment](docs/CONTRIBUTION.md): stock/cap400 gains 5.67%; padded Q3 adds 2.89% at about 3 GiB extra VRAM.
- [Submission-size profiling and follow-up](docs/SUBMISSION-CAP.md): +8.43% scoped whole-configuration gain; original clock-matched failure retained, natural clocks/power reported.
- [Native Q6 alignment and scale exchange](docs/Q6-NATIVE.md): exact operators and smaller shaders, but no qualified streamed gain.
- [Combined smaller-fusion follow-up](docs/FUSION-COMBINATION.md): graph-cached options, correctness checks and independent matched-load confirmation.
- [Q3 host-overhead profiling](docs/Q3-HOST-COST.md): confirmed scoped+3.4% native-path gain after reducing configuration-lookup overhead.
- [Q3 weight-alignment prototype](docs/Q3-PAD112.md): operator gains and exact model checks; the newer host follow-up establishes a scoped gain.
- [Experiment catalog](docs/EXPERIMENTS.md): the main lines of investigation.
- [Smaller fusions and shader roadmap](docs/ROADMAP.md): what the evidence suggests trying next.
- [Native fusion rounding diagnosis and corrected audit](docs/NATIVE-FUSION.md).
- [Shuffle8variant, source and model checks](docs/SHUFFLE8.md).
- [Native quantizer shuffle checks](docs/NATIVE-QUANT-SHUFFLE.md).
- [Native Q3 correction and precomputed-sum experiments](docs/NATIVE-Q3.md).
- [Combined smaller-kernel checks and overlap](docs/COMBINED-NATIVE.md).
- [Production-backend quantizer/Q3 operator and target-logit checks](docs/PRODUCTION-NATIVE.md).
- [Production SwiGLU fusion and all-three model checks](docs/PRODUCTION-FUSION.md).
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
