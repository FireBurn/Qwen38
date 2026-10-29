# Next Qwen work after confirmed native improvement

All prior jobs are terminal. Latest scoped result: host-cost-qualification.json, +3.43%steady native decode vsunmodified stock,24runs/all6blocks matched. Keep qualified-20261029 immutable; use new directories for changes. Reproduce with run_q3_pad112_qualified_once.py through private GPU guard. CPU/build load remains authorized; no quiet gate.

Next useful smaller-fusion work: hoist remaining per-fused-call GLU group-limit/coalescence configuration reads to graph setup, using the qualified v2 source as a preserved baseline. Existing nq_quantize reads GGML_VK_NATIVE_GLUQ_GROUPS per call, and eligible coalescing still reads its flag per pair. On this LLVMlibc benchmark environment a getenv costs~2.5us. Preserve default16 and explicit1..136 bounds, runtime changes between graphs, graph consumer/alias proofs and quantizer rounding. Rebuild all3hostTUs if context fields change. This is a hypothesis, not yet implemented or measured.

Then test the actual combination: aligned Q3 arena plus SwiGLU→Q8 fusion and/or quantizer shuffle. Older all-three tests found no gain before these host-overhead fixes. Do not sum microbenchmark percentages. Existing Q3 integer-correction modules use110-byte layout; enabling their old selector does not automatically modify the112-byte padded shader. Build a separately validated combined module if testing that arithmetic change.

Any new configuration: capped operator parity/guards, target-bit audits, native control, then fixed stock A/B with telemetry/runtime provenance. The successful matched-stock protocol fixes24arms, selects blocks only by predeclared load/runqueue/clock criteria, needs>=4blocks and retains all evidence. No performance-based extra runs.

Broader validation still valuable: longer populated KV, additional prompts and memory-budget fallback. Current gain applies to this27B Q3LynnStyle model,R9700,private7kdriver,.27/.7core,greedy,MTPmax1,4kctx,q8KV. The immutable-only contract and3GiB extra reservation remain; no general mutable-weight support.

Mega/FA goal remains open. Port aligned weight access or other proven component changes only in an isolated mega branch, with its own model audit and same-stack native anchor. Existing persistent mega still has native matrix-performance/resource/barrier gaps. Never replace current scoped native result with an unverified mega claim.

Do not touch Claude checkout,production libraries,original model,desktop,clocks,affinity. GPU jobs serial through private guarded scheduler. No upstream PR/messages authorized; public FireBurn/Qwen38 evidence updates are authorized.
