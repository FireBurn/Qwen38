# Sparse attribution follow-up

Plan only; no new shader/backend implemented yet. Preserve original scope: explain and reduce mega body gap with integrated FA.

Existing STATUS demonstrates dense16-WG/all-record sampling perturbs throughput and spills SGPRs. Do not reuse it unchanged. It used an older pre-native-RMS shader; new work must derive from qualified native_order.comp and current backend.

Proposed differences:

- Probe deterministic hash-selected1/64 tape records and four physical groups (first,last,two interior), rather than16groups/everyrecord. Rotate the deterministic hash with graph sequence so reused DAGs do not always sample the same operators.
- Keep separate profile storage; do not reuse barrier counters or tape fields. At four samples/two64-bit clocks, use64bytes per record and a bounded16MiB device ring. Validate capacity/owner/device before enabling capture. Disabled capture passes zero address.
- Zero profile storage once before capture; retain CPU copies of selected tape metadata and ring offsets. Export only known-selected records and explicitly detect missing writes. Do not interpret unwritten holes.
- Copy requested graph/segment profile regions with normal transfer/host visibility barriers. Defer CPU export/device wait until teardown after timed generation, instead of waiting and formatting JSON at every graph begin. Final selected graph must be exported too. Require one logical device/verified ownership; clear state at backend teardown.
- Explicitly query/enable VK_KHR_shader_clock as the old prototype did. ScopeDevice clock avoids relying on a clock/frequency conversion. Compare within-record elapsed ticks; never sum overlapping WG phase envelopes or label barrier wait as removable work.
- Keep all interpreter math, barriers and submission boundaries unchanged. Start<=16groups; canonical numerical gates then192 with existing capacity margin.
- Matched parent/instrumented-off/sparse-on controls must quantify observer cost. Retain profiler only if overhead is small enough to resolve the actual mega gap; no precise operation attribution if the observer changes scheduling materially.

Need implementation review: current global mega state can serve multiple backend contexts on one device. Capture ownership and teardown must be explicit, rather than retaining stale buffer pointers across context destruction.
