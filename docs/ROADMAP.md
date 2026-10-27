# Smaller fusions and individual shaders

## Assessment

**Yes: focused native-path fusions and individual shader improvements are a better next allocation of effort than enlarging the all-operation mega kernel.** This is a prioritization judgment from the evidence, not a promise of a gain. Several obvious fusions were already tried and did not produce a model win.

A useful smaller fusion should remove a material read/write, dependency, or dispatch while retaining specialized resource allocation and native scheduling. A smaller persistent interpreter that still carries a common register budget and frequent grid barriers may reproduce the same problems.

## Ranked experiments

| Priority | Candidate | Why it could help | Existing evidence / trap | Acceptance test |
|---|---|---|---|---|
| 1 | Native SwiGLU→Q8 quantization | Computes gate activation and packed activation together; can remove one stage and a reload | Mega version is exact; new native prototype now passes focused operators and captured model audits after matching compiler settings (see native fusion report); memory saving alone is small | Same C1/C2 guards and outputs; standalone native fusion vs original native path; full model gain beyond drift |
| 1 | Matrix shader scheduling and data reuse | Matrix work dominates; optimize Q3/Q4/Q5 with model-weighted mixes | Four-family synthetic mix overweights Q6; static instruction counts are not executed counters | Per-type C1/C2/tails/bias tests, resource and memory-access evidence, model-weighted stream test and full decode |
| 2 | Q6 C2 row packing / scale exchange | Reduce live accumulator state or LDS handoff | One-row is now exact; more tiles/input loads can cost more; previous shuffle variant did not establish a gain | Native one/two-row implementations under the same copy path, odd rows and K tails, full model |
| 2 | Attention epilogue fusion | Fuse reduction output gating/scale/packing where consumers permit it | FA is a limited fraction at short context; preserve split-K merge arithmetic and causal masks | Short and long KV, GQA ratios, mask/query tails, actual context-length curves and full model |
| 2 | Recurrent preparation within GDN | Fuse gates, beta sigmoid and head-local preparation without global barriers | Gate preparation and normalization were already investigated; some additions raise resource use | Repeated tokens, state snapshots, speculative rollback/rejection and long continuation checks |
| 3 | Native RMS/scale/Q8 preparation | Potentially removes intermediate vectors without duplicating preparation in every matvec worker | Claude's native RMS/Q8 experiment was reverted after no gain; do not simply repeat it | Identify what changed in the cost model first; exact rounding and conservative alias/consumer checks |
| 3 | Reusable command/descriptor templates | Preserve native kernels' specialization while reducing CPU recording work | Full single-submit mega execution got slower; GPU-generated commands still need dependency barriers | CPU recording time separately from GPU execution, changing addresses/KV depth, total accepted-token latency |

## Bigger-picture constraints

The inspected model has about **14.35 GB of target-body weight payload**; FFN gate/up/down account for about **66.8%** of it. Q4_K, Q5_K, Q3_K and Q6_K contribute about 32.7%, 28.7%, 20.8% and 17.4% respectively. Tensor payload is not measured DRAM traffic, and speculative verification can amortize a pass across accepted tokens.

The C2 SwiGLU/quantization fusion avoids only about 139 KB of float reload per pair. Even 64 pairs would be about 8.9 MB, versus gigabytes of weights. Its larger opportunity must come from reduced stage/synchronization cost. That is why a nice local percentage may make a small difference to the full model.

The 1.35 GB Q8 output projection is important, but the bounded-head work already shows the danger of optimizing an infrequent substage: a roughly 4.7% head-component gain was estimated at roughly 0.2% of model time in that configuration.

## How to combine changes

1. Establish an unchanged native baseline for the exact current production revision and model.
2. Add one specialized native fusion. Measure both the affected component and accepted-token throughput.
3. Add the next independent change and run baseline/A/B/A+B in symmetric order.
4. Inspect combined VGPR/LDS/spills and output correctness; do not inherit either candidate's resource qualification.
5. Test long context and speculative acceptance/rollback before changing defaults.

Prefer small shader variants selected by captured shape/quantization and justified guards. Keep native fallback and correctness observability. Do not trade model quality, weight precision or recurrence semantics for a kernel result without labeling that a separate quality experiment.

## What not to repeat without a new reason

- Blind barrier removal or grids that can exceed conservative residency.
- Fully static striped work assignment or larger atomic chunks as generic wins.
- Counting a smaller VGPR number as higher measured occupancy.
- Treating FP16/bfloat16 conversions, norm reordering or fused contraction as automatically bit-preserving.
- Applying HIP/LLVM patches to an ACO-generated Vulkan shader and expecting direct codegen changes.
- Reapplying tiled concat, integer-loader, split-K or other changes already in the production baseline.

## Research worth following

Tile-dependency scheduling from Cohere/Mirage, recurrent-operation fusion from Flash Linear Attention, composable attention states from FlashInfer, RDNA-oriented FA layouts, and LLVM/ACO scheduling work are useful design references. They are not drop-in R9700 speedups. See [references](REFERENCES.md) and the historical [research notebook](../archive/research.md).
