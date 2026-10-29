# Bounded Q3 gate/up/SwiGLU fusion

**The fused operator is numerically exact in the tested cases and reduces focused GPU time. A full-model speedup remains unproved.** The preserved Q3/cap400 configuration remains the qualified option. This is a bounded FFN kernel, not a whole-model mega kernel or a fusion with Flash Attention.

## What changed

A read-only graph audit found39 eligible Q3 gate/up pairs per target graph: adjacent matrix multiplications sharing an activation, each with a unique consumer feeding split SwiGLU. The prototype assigns a wave to the gate/up reductions for one output row, then computes `a / (1 + exp(-a)) * b` after reduction. C1/C2 retain the original K iteration, dot-product accumulation and subgroup reduction orders. Intermediate gate/up tensors stay in registers instead of being written and read through separate buffers.

The kernel still reads both weight matrices. Its64-thread workgroups are independent; there is no inter-workgroup barrier, persistent scheduler or command replay. Both C1 and C2 use48 allocated VGPRs with zero spills, LDS and scratch. Static instruction counts are archived, but they include complete shader control flow and are not retired-instruction counts or speed measurements.

The native reference is two frozen padded-Q3 matmuls followed by the exact production SwiGLU module. The extracted module's bytes were also located in the preserved qualified library. The timing reference permits the independent gate/up kernels to overlap; it does not artificially serialize them.

## Operator evidence

All576 bounded comparisons, with at most16 workgroups per dispatch, passed exact output-byte comparison, scalar matrix checks, input immutability and guards. A further128 comparisons covered larger shapes through17,408 workgroups, including K5120/R17408 and K17408/R5120, C1/C2, four activation patterns and both gate/up orders. Native matrix scalar checks sample first/middle/last rows at large shapes; native GPU comparison covers every output. No new GPU errors occurred.

A fixed96-arm GPU timestamp screen used K5120/R17408, six alternating ABBA/BAAB blocks per condition,1024 operator repetitions per arm, and the same weight buffers for both modes. Activation quantization is outside both modes.

| Condition | Fused operator time change | Descriptive95% interval |
|---|---:|---:|
| C1, one replica | −12.82% | [−19.00%, −6.17%] |
| C1, eight rotating replicas | −2.57% | [−3.82%, −1.31%] |
| C2, one replica | −10.50% | [−13.71%, −7.18%] |
| **C2, eight rotating replicas: primary** | **−3.87%** | **[−5.65%, −2.05%]** |

Negative time change is faster. These are focused operator results, not token rates. Six blocks, temporal correlation, DVFS and the gap between a microbenchmark and the full model limit generalization. Per-arm CPU, clock, power, build and sensor data are descriptive, with no formal clock/load gate in this screen. No equal-clock efficiency claim follows.

## Private host integration and numerical checks

Only the private backend changes. All three host source files were rebuilt against the same private context header. The candidate uses the native activation quantizer and padded immutable-weight cache. It rejects unsupported shapes/types/precision, views, misalignment, extra consumers and output overlap with either weight or the activation. It checks both padded weights before eliding nodes; a failed eligibility or budget check retains the native path. The existing fused-operation overlap and dependency tracking remains in place. Only the final SwiGLU output is marked as written. Pipelines and retained buffer references belong to the context and are released after synchronization. Actual matmul FLOPs remain counted when nodes are elided.

The short audit compares fresh stock, preserved Q3/cap400, new inactive and new active paths. Coding, maths, populated-KV and KV-boundary checks compare inactive/active paths against their native references. All five active cases match **630 unique requested full-vocabulary target-logit rows**, tokens and acceptance counters, with actual positive fused-dispatch counts. The short active case executes780 fused dispatches; its inactive controls execute none. No new GPU errors occurred. This is target-row/output evidence, not every internal draft tensor or arbitrary-context qualification.

Some inherited audit fields and labels refer to reader modes or native command observation. Reader-oracle fields are unused zeros; the `pair_mode`, actual shader paths, pinned assets and dispatch counts define this experiment.

## Full-model under-load discovery did not qualify

The fixed24-process,512-requested-token test compared the preserved Q3/cap400 library against the private active fusion at cap400. The model, native padded/repack shaders, core/common libraries, private driver, MTP policy and one-thread CPU settings were fixed. All24 processes produced the same513 tokens,279 drafts and234 accepts, with no new GPU errors and valid required telemetry.

The all-six-block raw estimate was **+9.38%, descriptive95% interval [−2.13%, +22.23%]**. Only **two of six blocks** passed the preset CPU/build/runqueue matching rules, below the required four. Their effects were +0.81% and +9.58%; two blocks do not support a qualified interval or adoption.

The largest raw block effect, +32.11%, coincided with CPU means of86.16% for control versus64.66% for candidate, and substantially fewer build processes in the candidate arms. Other blocks also failed workload matching. This is a concrete example of background compiles inflating an apparent speedup. CPU averages and process counts cannot fully characterize memory contention either.

No samples were added to rescue the result. The independently declared confirmation stage did not run because its discovery trigger failed. The raw +9.38% is not a supported model gain, and historical configuration percentages must not be added to it. Keep the preserved qualified configuration; the pair fusion remains experimental.

## Evidence

- [Initial plan](../archive/isolated/q3-pair-glu/PLAN.md), [graph audit](../archive/isolated/q3-pair-glu/graph-audit-summary.json), [exact production-GLU module verification](../archive/isolated/q3-pair-glu/production-glu-verification.json).
- [Shader builder](../archive/isolated/q3-pair-glu/build_operator.py), [complete shader source](../archive/isolated/q3-pair-glu/shader/mul_mat_vecq.comp), [bounded checks/resources](../archive/isolated/q3-pair-glu/operators/checks.json), [larger checks](../archive/isolated/q3-pair-glu/stress/checks.json).
- [Operator screen protocol](../archive/isolated/q3-pair-glu/TIMING-PLAN.md), [all96 timing arms and telemetry summaries](../archive/isolated/q3-pair-glu/timing/20261029T133758Z/analysis.json).
- [Host integration plan](../archive/isolated/q3-pair-glu/HOST-PLAN.md), [host patch](../archive/isolated/q3-pair-glu/host.patch), [host builder](../archive/isolated/q3-pair-glu/build_host.py), [five-case qualification](../archive/isolated/q3-pair-glu/qualification-summary.json).
- [Model discovery protocol](../archive/isolated/q3-pair-glu/MODEL-TIMING-PLAN.md), [complete model report](../archive/isolated/q3-pair-glu/model-timing512/20261029T135426Z/confirmation-analysis.json), [unused conditional confirmation plan](../archive/isolated/q3-pair-glu/MODEL-CONFIRMATION-PLAN.md).

The archive contains source, patches, compile commands, manifests and selected JSON/JSONL evidence. Models, binaries, raw logits and shader caches remain local. Rebuilding requires the pinned original llama.cpp/private build inputs; this is an experimental evidence archive, not a standalone deployment package.

## Eligibility and fallback witnesses

A separate GGML client compared frozen, inactive and active paths over25 normal cases and four input patterns, plus two cases with fusion disabled in fresh frozen/active processes. All final outputs and requested intermediate outputs matched byte for byte. Valid and reversed gate/up cases at K2048 fused in C1 and C2; the active normal run recorded16 dispatches. Different activation pointers, extra consumers, preserved intermediate outputs, weight/input views, other or mixed quant types, explicit precision, unmarked weights, activation/output alias and C3 all used the native path. Disabled fusion also recorded zero pair dispatches. No new GPU errors occurred.

The first witness used K256 and incorrectly expected C1 fusion. AMD's native MMVQ policy rejects C1 below K2048, so that fallback was correct; all three completed output files matched and no driver errors occurred. The failed harness expectation and source are preserved. The revised K2048 inputs exercise the intended positive C1 route; the alias case remains K=R256. This was a test-expectation correction, not a numerical or performance failure being hidden.

[Witness protocol](../archive/isolated/q3-pair-glu/ELIGIBILITY-PLAN.md), [complete witness results](../archive/isolated/q3-pair-glu/eligibility/comparison.json), [case-level counts](../archive/isolated/q3-pair-glu/eligibility/checks.json), [preserved initial expectation failure](../archive/isolated/q3-pair-glu/eligibility-attempt1-policy-expectation/observed-evidence.json).

## Separate resident diagnostic: tighter load matching, still inconclusive

A separately declared experiment kept the unchanged private host, model weights and contexts resident. It ran one unmeasured active warmup followed by24 alternating128-requested-token generations in six ABBA/BAAB blocks. Both model memories were cleared and samplers/speculators recreated between arms. Target and draft contexts were explicitly synchronized at encoding end, the warm/steady boundary and generation end. Only the fusion flag changed; this compares the new host's inactive and active paths, not the preserved frozen binary.

All25 generations matched the native130-token reference and acceptance counters, with no new GPU errors. **All six blocks** met the preset CPU/build/runqueue and telemetry rules. CPU utilization was approximately100%, build count approximately17 and runnable count approximately28; background compilation continued.

Full-generation time changed by **−0.60%, descriptive95% interval [−1.69%, +0.51%]**. The secondary steady-window result was **−0.36% [−1.41%, +0.70%]**. Neither interval establishes a gain. These results are not pooled with the failed fresh-process dataset or treated as its conditional confirmation. No arms were added. One active-only warmup can leave initial inactive descriptor allocation cold; all arms remain included. Context state, ordering and temporal correlation also limit inference.

A rough budget helps explain the small effect: the earlier intrusive grouped profile attributed14.94% of recorded GPU time to the Q3 gate/up pair. Multiplying that share by the separate3.87% operator time reduction gives approximately **0.58% of total GPU time**, assuming all other costs and overlap remain unchanged. This combines different diagnostics and omits CPU, queue and DVFS effects; it is a scale estimate, not a measured end-to-end prediction or proof of the bottleneck. The observed resident estimate is small enough to be consistent with that budget.

[Resident protocol](../archive/isolated/q3-pair-glu/RESIDENT-PLAN.md), [complete resident analysis](../archive/isolated/q3-pair-glu/resident/20261029T191335Z/analysis.json), [runner with explicit synchronization](../archive/isolated/q3-pair-glu/resident-runner.cpp), [coverage budget and assumptions](../archive/isolated/q3-pair-glu/coverage-budget.json).
