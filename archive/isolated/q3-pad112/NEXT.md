# Next Qwen work after arena investigation

Completed results are in arena-model-under-load512/20261028T233122Z and arena-prompts128; all jobs are terminal. CPU/build load remains explicitly authorized; no quiet gate.

The one-arena resident128token test has a promising+1.8198% private-control contrast, descriptive95%[+0.2471,+3.4172]%, six comparable blocks. It is not an unmodified-stock/compile-saturated/long-context result. Background load differs from the separate-buffer trial, so allocation count is only a hypothesis.

Next priority: profile padded-path host cost without per-call mode switching before more GPU arithmetic tweaks. The enqueue-only mixed-mode diagnostic costs~1.2ms more CPU on pad (7.65vs8.85ms); this includes other driver/wait work and switching may affect descriptor reuse. Do not assume it is the cache lookup. Add opt-in scoped counters or use read-only perf if available; do not change kernel security settings or desktop/affinity/clocks.

Investigate removing duplication/dispatch overhead by storing one backend-specific padded representation in existing weight allocations. That could avoid an extra3GiB cache/BO and a hot cache selector, but requires correct get_alloc_size, upload/download/partial writes, views, prefill/MMQ/dequant/get_rows pipelines and native-interface conversion. No such implementation exists yet; do not globally override all Q3 shaders while native-format buffers remain. Study upstream OpenCL Q3 conversion/restore and SoA commit d04eb29e8b87328cfb4463bc75796a26e880b8e0. Keep the model working with capped operator tests and full target-bit audits.

Lower-risk next shader: combine aligned112-byte Q3 blocks with the already qualified local integer Q3 correction, using existing arena host and a new shader directory. Keep original pad16 controls untouched. First compile/validate and <=16WG production-geometry oracle/parity, then target logits and fixed A/B. Additional math gains may not overcome host overhead.

A tiled SoA layout could align quant/high-mask/scale planes without per-block padding. It is an untested proposal. If testing78allocations versusone, use the same workload/context and explicit VRAM budget; different-load runs do not establish allocation causality.

All jobs from this round finished; do not wait on or restart old quiet queues. CPU/build load is authorized; GPU jobs serial through private guarded scheduler. Work only inside megakernel-review; preserve Claude, production libraries and original model.
