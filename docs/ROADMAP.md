# Smaller fusions and individual shaders

## Assessment

**Yes: focused native-path fusions and individual shader improvements are a better next allocation of effort than enlarging the all-operation mega kernel.** This is a prioritization judgment from the evidence, not a promise of a gain. Several obvious fusions were already tried and did not produce a model win.

A useful smaller fusion should remove a material read/write, dependency, or dispatch while retaining specialized resource allocation and native scheduling. A smaller persistent interpreter that still carries a common register budget and frequent grid barriers may reproduce the same problems.

## Current milestone

The [Q3 host-overhead follow-up](Q3-HOST-COST.md) measures+3.43% steady native-path decoding versus stock in24matched runs. The useful combination is aligned weight loads plus avoiding repeated configuration checks; neither static instruction counts nor the first cache prototype alone established that result. Broader contexts/prompts and additional fusion combinations remain separate work.

## Ranked experiments

| Priority | Candidate | Why it could help | Existing evidence / trap | Acceptance test |
|---|---|---|---|---|
| 1 | Native SwiGLU→Q8 quantization | Computes gate activation and packed activation together; can remove one stage and a reload | Mega version is exact; new native prototype now passes focused operators and captured model audits after matching compiler settings (see native fusion report); memory saving alone is small | Same C1/C2 guards and outputs; standalone native fusion vs original native path; full model gain beyond drift |
| 1 | Native graph planning/recording reuse | Avoid repeated host work while keeping native shader arithmetic; observer finds 767 repeat graph records | No replay or speed proof; descriptor, transfer, pool and fence ownership must remain correct | Profile planning cost, then strict metadata invalidation and fresh-native KV/rollback checks before timing |
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

## Native fusion-plan cache follow-up

[CPU planning reuse](NATIVE-FUSION-PLAN.md) passes five exact target-logit cases (530 rows), 1,379 CPU invalidation checks and real GPU metadata mutations. The fixed 24-run under-load model test establishes no incremental gain: descriptive −6.77% [−17.69%, +5.61%], only one of six external-load-matched blocks. Keep the preserved qualified configuration. The separate fixed resident diagnostic finds graph CPU time −23.05% [−30.89%,−14.32%] descriptively, but full generation time +0.40% [−5.91%,+7.14%], only two matched blocks. CPU savings have not established faster generation.

## Native submission-budget follow-up

[Native divisor20](NATIVE-SUBMIT-BUDGET.md) retains native commands and shaders while reducing graph batches in five exact-output cases (530 rows). Fixed24 discovery has four external-load-matched blocks and +0.75% steady speed [+0.25%,+1.26%]. The independent24 confirmation has zero matched blocks and inconclusive raw +2.53% [−7.90%,+14.14%]. No confirmed gain or adoption; preserve the qualified configuration. A CPU timeline separates graph and transfer/synchronization submissions.

## Transfer-attribution follow-up

The [native transfer observer](NATIVE-TRANSFER-OBSERVER.md) attributes1,850 of4,579queuecalls per short decode to synchronous tensor sets, with643.6msinclusive wall/91.1msCPU on average. All six native generations match129tokens/74drafts/55accepts; no GPU errors. This is a measured optimization target, not a speedup. Identify tensor names/flags before designing retained staging that preserves immediate source capture and completion-aware recycling.

## Input metadata, native defaults and immutable rotations

[Metadata attribution](NATIVE-TRANSFER-OBSERVER.md#tensor-metadata-and-follow-up) found repeated fixed Hadamard inputs. The [private constant cache](NATIVE-CONSTANT-ROTATION.md) passes530targetrows and six repeated-clear generations, with444fewer uploads/queuecalls. Separately, [mapped VRAM](NATIVE-MAPPED-VRAM.md) passes530rows and removes2,442queuecalls, with fixed48-run discovery+28.60% [+25.91%,+31.35%] over the old harness in eight matched blocks, separate48-run confirmation+28.31% [+22.37%,+34.53%] in five matched blocks. All96runs preserve native tokens/counters with no GPU errors. Natural GPU clocks/power rise; direct stock-default comparison remains pending, with no equal-clock/default-stock claim. Restoring this existing native default corrects a [harness override](BASELINE-ENVIRONMENT.md); prior stock comparisons are scoped to their archived environment. No new shader/default-stock/mega-kernel gain is claimed from these mechanism checks.

## Direct native-default controls

[Stock100, stock400 and padded-Q3/default400](NATIVE-DEFAULT-BASELINE.md) pass530targetrows per mode (1,590mode-row checks), with matching native tokens/counters and no GPU errors. All four legacy allocation/queue overrides are absent. The predeclared72-run primary combination and secondary cap/padding attribution is in progress; no default-stock speed gain is claimed yet.


Latest priority and completed confirmation: [current status](CURRENT-STATUS.md). Cap100Q3 is independently positive; cap400combination rejected. Next: validate raw callback audit, then restricted greedy/backend controls before hierarchical argmax kernels. Mapped CPU fusion cache remains a separate deferred interaction.


Widerargmaxindependentlyconfirms+2.35%native-pathgain; see[currentstatus](CURRENT-STATUS.md). Next:newprivateQ3padding/native100+widecomposition, correctnessbeforetiming, noaddingindependentpercentages. Existingqualifiedcomponentsunchanged.
