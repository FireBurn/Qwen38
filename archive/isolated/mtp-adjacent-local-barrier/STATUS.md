# Adjacent local barrier experiment

Goal: improve the unified mega body, preserving integrated FA, exact native RMS summation and current device memory visibility protocol.

## Change and proof obligation

Only the final workgroup barrier in the interpreter loop becomes conditional when the next immutable tape record is an explicit global gridbar. All other local barriers, the final-record barrier, gridbar's two workgroup barriers, device Buffer AcquireRelease fences and atomic acquire-release arrival/wait remain unchanged.

Every invocation finishes its operation stores, executes its own gridbar device fence, then reaches gridbar's first workgroup barrier. That barrier waits for all invocations before the elected invocation publishes arrival. The release counter and acquire waits, final workgroup barrier and final device fence retain cross-workgroup visibility. Tape lookahead is workgroup-uniform and immutable. Source hashes and scope are in source-proof.json. A proof argument does not replace device/model checks.

## Qualification

- Build session63710 terminal0: glslc, Aliased descriptor annotations before optimization, spirv-opt and spirv-val. Allocator emitted nonfatal size-class population messages; authoritative build completed successfully. No driver changes.
- First16 session55123 terminal0: seven shapes, native/parent/candidate, six input patterns each. Every candidate output bit native-exact, last12 graphs remain mega. 96VGPR,16KiBLDS,0scratch, no VGPR spills. Conservative capacity256groups retains64spare at192.
- Model session10093 terminal0: candidate mega16/head16 and mega192/head192, same private threshold core/backend and frozen RADV. Both reproduce canonical audit SHA873abacccc270bc1a0669f62ac831dcc14ace252db9f60bbc0006a7c7b84dec2;34tokens,19drafted/15accepted. All normalized hidden vectors, full target logits and sampled draft10 IDs/scores exact. Integrated mega fusion active.

## Current job

Matched full-model throughput session24778 is running through run_private_guarded_batch.py. Five modes then reverse,128requested tokens each: nativeCPU,nativeGPU,nativeBound,megaParentBound,megaCandidateBound. Common threshold core/backend/head, frozen RADV, exact tokens/counters checked, total decoder/steady/encoding/process costs and CPU/GPU/compiler telemetry retained. No speed or quiet claim until terminal results and telemetry are inspected. Last process snapshot before launch showed no background compiler processes; this is only launch evidence.

No installed files, Claude sources, clocks, affinities, priorities or power settings changed. No other own GPU job should launch while24778 is active.

## Terminal throughput results

Session24778 terminal0, model-throughput/20261026T100807Z:128requested/129actual tokens all identical,74drafted/55accepted. Means t/s nativeCPU45.7886,nativeGPU46.2428,nativeBound46.5428,megaParent40.6564,megaCandidate41.1614. Candidate+1.242%vsparent; parent drift1.328%,candidate0.161%. Zero background compiler/JVM processes throughout active samples; CPU~3-4%, GPU clocks~3.1GHz. This quiet telemetry is materially different from earlier CPU~100%,15-17builds,~1.6GHz runs. Cross-run difference confirms compile load is a substantial confound, not causal isolation of its individual effects.

Longer paired512 session67313 terminal0: paired512/20261026T101025Z/summary.json, ABBA,513actualtokens,279drafted/234accepted,496steady tokens each. Means parent43.4873,candidate43.5414t/s, +0.1244%. Parent drift0.192%,candidate1.085%. All tokens/counters exact and zero background compiler processes. The earlier1.24% improvement is not confirmed. Do not promote this shader; no robust whole-model gain. All own GPU jobs terminal at this entry.

Optimized SPIR-V parent/candidate have132ControlBarrier and15MemoryBarrier instructions each; conditional branches2169/2171. Source removes dynamic adjacent local barrier executions, not the static barrier instruction count. Micro resource code493996/494000bytes,96VGPR,1SGPRspill,16KiBLDS,0scratch in both. Small code/resource difference and no confirmed gain do not justify broader fence relaxation.

Next broader baseline job prepared separately: ../mtp-production-throughput, private timing runner compiled against matching frozen production aa8 common0.7/core0.7/GGML0.27 with original source/header manifests verified. Adds the same warm/steady timing window and validates core/common/backend/driver paths. Original0.27runner and all frozen libraries untouched. Production default activation policy retained; cross-stack result cannot be attributed to a single shader.
