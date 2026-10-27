# Resource target beyond claim batching

Current reference: native quantized matvec audit48VGPR/0LDS, unified combined keep72VGPR/12KiB. The settled streaming gap is not closed by the existing256WG launch. Do not treat this as measured occupancy.

A meaningful next resource target is60VGPR **and**8KiB LDS while retaining FA in the same shader. Under the existing hardware bound formula,60VGPR permits6WG/CU and8KiB permits8WG/CU: combined384WG bound, allowing320launched with64spare. Current72VGPR/12KiB bound320 permits256launched with64spare. Either change alone may be insufficient. This is a hypothesis, not a launch authorization or forward-progress proof.

Potential FA design: preserve V staging in8KiB LDS, move Q and probability tiles to disjoint per-WG private global scratch. Q is constant across the KV loop; convert and scale it once, rather than once per KV block. Keep K and score storage at offset0 in disjoint phases, respecting existing completion barriers. A mask reduction can occupy the same region only with verified lifetime boundaries. Q and probability cooperative loads can use storage-buffer arrays, as current K/V direct paths already do. Cross-invocation scratch stores require explicit workgroup-scoped buffer visibility before cooperative reads; a shared-only barrier is insufficient.

To reach60registers too, consider rowwise softmax using scalar old-max/new-max/sum and immediate output decay, writing rounded half probabilities directly to the private probability tile. Preserve each row's exact exp and accumulation order, f16 rounding before the sum, and original PV order. This may reduce live Mf/Lf/staged_probability arrays. Previous early-save and row-decay variants alone did not achieve a resource benefit; this proposal changes probability storage as well and remains unimplemented.

Costs: additional cached global traffic may make FA slower. A whole-model win is possible only if matrix residency/latency hiding gains exceed that cost; require isolated FA and matrix tests plus full model throughput. Do not assume scratch is free because compiler scratch is zero.

A new private scheduler filter would be needed for8KiB: current sched-keep-occupancy-12k intentionally does not match it. Require numerical microtests, full masks/causal/prefix tests, resource/ISA audit and16WG model qualification before any larger grid. Current queued adaptive claim tests remain independent.

Correction from authoritative occupancy-audit.json: wave64 VGPR allocation granularity is12, so64rounds up to72. The real next target is60allocated VGPR (not64) with8KiB LDS. The prior idealized64calculation omitted that rounding and must not authorize any larger launch. All experiments so far stayed<=16 or previously qualified72/256 configurations.
