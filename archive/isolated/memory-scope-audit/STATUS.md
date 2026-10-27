# Memory scope and profiling audit — 2026-10-23

CPU-only source investigation; no shader or driver modifications and no GPU probes.

The private RADV source radv_pipeline.c:314 invokes nir_lower_memory_model. That pass replaces MakeAvailable/MakeVisible barrier semantics by ACCESS_COHERENT on relevant stores/loads. Therefore moving visibility from individual accesses to explicit grid barriers is not by itself a way to obtain cheaper accesses with this compiler. Removing coherence without a replacement visibility proof would be incorrect.

AMD ac_shader_util.c:1085 ac_get_hw_cache_flags maps ACCESS_COHERENT or VOLATILE to GFX12 device scope, otherwise CU scope. This confirms a scope difference; it does not measure cache misses, cost, or establish an optimization. Immutable quantized weight views are already readonly/noncoherent. Mutable activation aliases require preserved cross-workgroup visibility. No scope weakening candidate is qualified.

Existing host supports GGML_VK_PERF_LOGGER, concurrent mode, and frequency. Default mode inserts timestamp and synchronization after each enqueued node; it perturbs scheduling and cannot provide an unmodified throughput comparison. Concurrent mode groups nodes. Mega has separate GGML_VK_MEGA_TS timestamps around dispatch, already used by FA harness. Native per-op attribution and mega dispatch totals can guide work, but neither alone includes host gaps or establishes end-to-end speed. Before enabling generic logger for mega, inspect interaction with deferred record/flush and query indexing. No device-clock shader instrumentation or profiling power-state change is needed for these timestamp facilities.

Next useful measurement: serial controlled diagnostic of reference mega GPU dispatch time against end-to-end token latency, then native operator attribution in a separate diagnostic. Keep performance benchmarks free of per-op synchronization, verify final fully mega graphs, and do not overlap quiet benchmark waiters.
