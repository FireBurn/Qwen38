# First two-query FA mega prototype passes

Six process cases pass: native Vulkan, original reference mega and new all-matvec+MQ prototype at KV256 and3328, head256/queryheads24/KVheads4, Q8 K/V, two distinct queries, causal F16 masks and explicit F32 accumulation. Every batch output and both serial outputs are bit-identical to native F32 and each other. Prototype final32graphs have zero native operations; reference still has one native MQ FA per graph.40graphs per process. First launch physical grid16. Backend/frozen driver mappings self-verified;guard exited0 and resumed exact quiet waiter.

Implementation reuses existing FA functions, descriptors and LDS, with uniform per-dispatch USE_MQ selected false for existing ID22 and true for ID36. Exact Flags34 alias added; all matrix parent entries retained. Code401236bytes versus parent381064;96VGPR/38spilledSGPR versus parent28, zeroVGPRspills,16KiBLDS,zeroScratch. No larger launch qualified here. Scalar spill/code-size increase needs mixed-operator regression and GPU performance checks before promotion.

Precision finding: default native half QK accumulation differs from fixed-F32 mega QK; matching explicit F32 removes the difference. Model attention builder requests F32. Current printed native/mega pipeline lookup key omits precision, so general host precision gating remains required. No global host or model-qualified shader modified.

Remaining: masks/queries/layouts/context/shape/changing-input coverage, causal future-token perturbation, all-matvec mixed-module regression, FA local timings, full-model teacher-forced2-vs1, SSM convolution/KV/cache/controller rollback and drafting acceptance/cost. No full-model MTP correctness, no token-speed claim, no installed or Claude modifications.

Mixed matrix regression completed: mixed/checks.json has20passing native/reference/prototype processes, all six target formats together at K5120/R3 and K17408/R7, eight changing input phases and consecutive same-pointer updates. Native fresh per-phase outputs, batch/serial equality and all prototype final24graphs entirelymega verified. Thus adding MQ did not change these tested matrix results. No performance conclusion follows.
