# Fused gate/up prototype

2026-10-25: implemented `build_shader.py`, producing unified parent shader with opt-in flag0x1000 on Q3 C2 opcode33.32row CTA uses four wave64 groups/four epochs, shared staging, original per-output arithmetic, shared packedB between both weights, preserved raw gate/up/GLU and separate Q8 output slot21. Other operators includingFA remain present.

GLSL compile, Aliased annotation, pre/post optimization Vulkan1.2 SPIR-V validation completed (build session14853 exit0). Optimizer emitted allocator page warnings but completed successfully. Manifest records exact sources/binary. No GPU execution, resource count or performance qualification yet. Host must enforce K5120,R17408,2columns,singlebatch,no bias and all slot nonoverlap constraints. Flag is not set by any current host.

`consumer-proof.cpp.inc` is an unintegrated conservative graph proof prototype: exact contiguous 17408x2 SwiGLU output, no exports/views/leaf aliases, exactly one later direct quantized down matmul consumer. This alone does not authorize fusion: captured PCs/descriptors, physical aliases, output buffer lifetime, down remap and native verification still required. Header not compiled yet.

Next: integrate host proof/tag and private dedicated Qscratch, preserve command-buffer ordering; synthetic rawG/U/F32GLU and byte-exactQ8 comparison at<=16WGs; resource gate before larger grids. No speedup claimed, existing known-good backend unchanged.


## Host consumer proof and resource gate completed

Private `host/ggml-vulkan.cpp` built via `prepare_host.py` (session25048 exit0). `consumer-proof.cpp.inc` now compiles. RAII tags track GLU and down tensors through record capture. `host/checks.json`:30logits/hidden records and17tokens byte-identical to reference; up to64direct single-consumer pairs per graph;486recorded GLU/quant/down sequences all match consumer tags over this run. Guarded run48138 exit0; original quiet waiter resumed. GPU fusion remains disabled.

Prototype fallback/resource probe83744 exit0,16WGs,64graphs/four in-place patterns/0–2biases, Q5K5120/R4097/C2 outputs byte-identical to native. This tests unchanged fallback, not fused branch. `resources.json`:96VGPR,38SGPR spills,16KiBLDS,zero scratch; code446956bytes versus parent425964 (+4.93%). No resource occupancy regression, but larger instruction footprint may cost performance and must be measured. No throughput claim. Guard resumed original waiter.

Next concrete implementation: private persistent Qscratch descriptor(s), strict captured gate/up/GLU/quant/down pattern and PCs/physical alias checks, opt-in fused flag, down-input remap, raw/F32/packed-byte exact synthetic checks at16WGs. Graph proof must be combined with captured same-segment dependencies, not used alone to delete barriers. Add lifetime/order proof for scratch reuse before any test.


## Actual fusion model audit passed; synthetic readback harness needs repair

Implemented `fusion.cpp.inc` / `prepare_fusion_host.py` / private `fused-host`:64 persistent39168byte packed-output slices registered before first dispatch (2.5MB total), one unique slice per fused FFN pergraph, no descriptor mutations while pending. Slice counter resets pergraph; existing first-segment full command-buffer barrier orders graph reuse. Same-segment exact eight-record pattern, exact PCs and GLUmode, full graph single-consumer tag, writable/input physical nonoverlap checks; preserves rawG/U/F32GLU; downB remapped, removes secondmatvec/GLU/quant andtwo internal markers; finalmarker beforedown preserved. Verify mode disables fusion until dedicated replay remap support exists. Max64 then safe fallback.

Fused model audit58123 terminal0:16WGs,351fusedFFNs,30full logits/hidden records and17tokens byte-identical to established reference. Guard resumed original quiet waiter. These results precede addition of test-only readback APIs; current host rebuilds50146/35961 terminal0 include those APIs but GPU arithmetic unchanged. Model audit needs rerun on final frozen host after harness fixes.

Synthetic harness `operator_bench.cpp` builds Q3 gate/up andQ4down, four in-place inputs (normal, signedzero,12.5x,1e-7x), rawG/U/F32GLU/down plus39168packedbytes perphase. `gateup_test_single_submit` resets only last_total_flops before testgraphs, avoiding native heuristic splitting tiny graph between gate/up; identical scheduling policy across native/parent/fused controls. Production model does not call this API.

Packed check30294 failed in NATIVE reference with hostSIGSEGV(-11), after458752F32bytes written, before any fused test. Guard resumed waiter. LLDB debug32578 and55085 terminal0 captured null-function call: frame1 `ggml_vk_ctx_begin+371`, frame2 `ggml_vk_buffer_read_2d+797`, frame3 `gateup_read_packed+139`. `readback-debug2.log` contains full stack. This is a private readback API/harness fault, not evidence of GPU kernel failure; no packed-byte correctness claim. Do not rerun uninstrumented until identifying null callback. LLDB exists (`gdb` absent). Next inspect ctx_begin machine code/null callback (possibly debug-label pointer, unconfirmed), then repair API, rerun exact packed tests. Preserve native crash artifacts. No active own jobs remain. Performance unmeasured.


## 2026-10-25: exact packed bytes; micro gain, no full-model gain

Readback root investigation: LLDB `readback-debug3.log` shows API in private `.24` image calling DispatchLoaderDynamic::init in a different `libggml-vulkan.so.0` image. Standalone executable has backend as startup DT_NEEDED dependency. Replaced dlopen(path,NOLOAD)+dlsym with dlsym(RTLD_DEFAULT), avoiding extra backend-image lookup/load. Explicit dispatcher initialization experiment did not fix crash and has been removed. Final packed check72518 passed with original dispatcher behavior. Earlier private host crashes are retained as failed-api2/3 artifacts; not GPU resets.

`packed-checks.json`: native, parent and fused all byte-identical for4changing input patterns (normal, signedzero,12.5x,1e-7x), rawG/U/GLU/down plus39168Q8bytes perphase,1991680bytes total.8graphs perarm;7fusedFFNs because initial descriptor-discovery graph falls back. Final harness supports optional GATEUP_BENCH_GRAPHS but defaults2iterations; default correctness rerun passed in batch64895.

`gpu-diagnostic/*/summary.json` contains symmetric6arm192WG GPUtimestamp diagnostic,512graphs/arm: parent0.325ms, prototypeoff0.3255ms, fused0.297ms (-8.62%vsparent,-8.76%vsoff). AllF32 andpackedbytesexact eacharm.511fusions/fusedarm, firstgraphfallback. Single FFN graph Q3gate/up+Q4down, syntheticquantizedweights larger than cache, four inputpatterns; under-load diagnostic, no full-model claim. This micro preceded linear proof/logging change; GPU shader remains identical.

Replaced per-candidate graph scan with one consumer collection pass (`consumer-proof-quadratic.cpp.inc` preserves predecessor). Graph proof and capture/fuser logging now gated by GGML_VK_MEGA_FUSION_LOG; throughput clears this. Finalhost build20605 terminal0. Batch64895 reran packed and fullmodel correctness then throughput, terminal0, original waiter resumed.

Final `model/comparisons.json`: off/fused ×Roman/C++ prompts at192WGs;213full logits/hidden records per mode, all tokens and acceptance counters byte-identical to qualified parent reference. No native ops in final12graphs, FA stays unified.

Full-model symmetric8arm throughput `throughput/20261025T121416Z/summary.json`, originalasyncMTPpipeline,129tokens allarms55accepted/74proposed identical: native44.7475t/s,parent38.88,prototypeoff38.37,fused38.167. Fused-1.834%vsparent,-0.529%vsoff, still14.706%slowernative. Control drift1.27–1.61%;3externalcompilers active,CPU~23%, generation clocks~3.1–3.2GHz. No adoption. Offvsparent combines proof overhead and module footprint; cannot attribute all of1.31% loss to compiler/code size. Fusedvsoff is below drift; no demonstratedfull gain despite8.6%micro improvement.

Next action: measure CPU proof/fuser time and target-verification GPUtimestamp totals under matched parent/off/fused controls, including actual full-model fusion counts, to explain why micro gain fails to translate. Do not extend Q4/Q5/Q6 variants blindly until this attribution. Global goal remains active; no faster-than-native endpoint achieved.


## Matched CPU/GPU graph attribution completed

`prepare_profile_host.py` derives separate `profile-host` from frozen fused host; no shader/math edits. Tracks per-graph CPUproof/fuser wall time and existing Vulkan GPUtimestamp query totals, number of fusedFFNs/segments. Profiling query wait changes pipeline overlap; do not use its end-to-end speed as adoption evidence. CPU walltime includes descheduling and timer overhead.

Build95459 terminal0. Profile first-check81569:16WGs,351fusions,30full logits/hidden records and17tokens exact. The subsequent analysis rejected its first full run because selector max(matmul.src1.ne1)==2 was wrong: internal matmuls have larger dimensions unrelated to decode batch. Preserved incomplete `profile-runs/20261025T121923Z`. Correct classifier:64two-column GLU nodes andgraph>=20; not maxinternalmatmul dimension.

Final matched6arm run94156 terminal0, `profile-runs/20261025T122039Z/summary.json`:69steady target verification graphs perarm, all129tokens55accepted/74proposed identical. All39eligibleFFNs fused everytargetgraph;20segments everymode. Means parent36.393653msGPU, prototypeoff36.860441ms, fused37.004775ms. CPUproofparent1.906us/off205.022us/fused203.123us; fuser walltime32.623/32.877/76.362us respectively. Fuser timing includes timer/disabled-call overhead; incremental fusion cost~43.5us. ParentGPU replicate36.394840/36.392466ms, off37.079629/36.641252ms, fused37.116446/36.893104ms. Fused-off0.144334ms(.392%) is below off/fused replicate drift; no established GPU speedup. Prototypeoff-parent~1.28%observed loss: code footprint/layout is a hypothesis, not proven attribution; proofCPUdoes not account for GPUtimestamp delta.

Threeexternalcompilers active allarms,CPU~23%; backgroundload stillprecludes quiet adoption. Original quiet waiter resumed. No newGPUcrashes. The readback helper hostfault was fixed via already-loaded global symbol lookup, not driver changes.

Next experiment should reduce module duplication rather than add format-specific clones: share existing Q3 C2 K-loop/reduction between paired and ordinary paths, append paired upaccumulation conditional onflag, share packedB. Consider one common WG job scheduler (8rowsnormal,32rowspaired) so SPIR-V inlining does not duplicate full gate loop in two wrappers. Normal C2/bias/tail cases must remain nativeexact, fallback for unsupported scheduling geometry. This changes ordinaryQ3 scheduling, so first16WG synthetic/tail/bias andresource gate required, then full213record audit, then streamedmicro and matchedfullthroughput. Do not assume smallercode is faster or remove required barriers. Current fused shader remains correct but unpromoted.


## Shared Q3 execution variant (benchmark in progress)

`build_shared_shader.py` produces `shared.comp`: replaces Q3C2 wrapper with one WG-uniform dynamic scheduler,8rows perordinary job or32rows perfused job; one existing Q3 K-loop and reduction, conditional upweight accumulation reusing packedB. Original bias handling retained; partial row tiles guard subgroup computation; no cross-WG dependency change. Fused Q8 pack retains exact native formula and separate scratch/down remap. FA and all42opcodes retained. OrdinaryQ3 scheduling changes, so this is a fresh candidate, not just code deduplication.

Compile39411 terminal0, Vulkan1.2 SPIR-V validation before/afteroptimization passed. FirstGPU64740 terminal0 at16WGs:4inputpatterns rawG/U/GLU/down/Q8all nativeexact,7fusedFFNs afterwarmup. `shared-results/resources.json`:96VGPR/38SGPRspills/16KiBLDS/0scratch,code431356bytes versus parent425964 (+1.266%) andoldfusion446956 (-3.49%).

Tail run69897:13cases passed, next childexit0 finished before/proc/maps polling confirmed paths; no numerical/GPUfailure. Faster sampling plus resume by completed authoritative case list fixed observation gap. An intermediate Python source-edit syntaxerror ran noGPU. Resume13395 terminal0: all26K/R/inputphase tailcases nativeexact andbatchvsseparatecolumns exact, final32graphs allmega.8biascontrol rows(native/shared across4shapes) each4in-place patterns×0/1/2biases, allnativeexact includingR4097. NoGPUcrashes.

Batch55946 serial benchmark chain: shared fullmodel off/fused×Roman/C++ at192WGs passed213full logits/hidden records per mode, tokens/acceptance exact; micro andfullthroughput follow in same guardedbatch. `shared-benchmark-batch.log` and`shared-results` hold outputs. Do not adopt until timing outcome known.


## Shared candidate rejected; WG scheduler control identifies dominant regression

Batch55946 terminal0, waiter resumed. `shared-results/gpu-diagnostic/*/summary.json`: parent0.3255ms, sharedoff0.4800ms, sharedfused0.4820ms (+48.08%vsparent). Allraw/F32/Q8bytesexact. Full symmetric8arms `shared-results/throughput/*/summary.json`: native44.597t/s,parent38.875,sharedoff35.4635,sharedfused35.1345. Sharedfused-9.622%vsparent,21.218%slowernative; tokens/acceptanceidentical. Control drift1.04–1.49%,3externalcompilers active. Code shrink alone did not help. No adoption.

Built `wg8_only.comp` via `build_wg8_control.py` (5690 exit0): paired flag compile-timefalse, so remove conditional upaccumulation/packing while retaining new ordinary WG8 scheduling. Test-only unfused control; never use with host fusion enabled (it deliberately ignores fusedflag). Same math/outputs, no normal subgroup scheduler preserved in this control.

Scheduler-control24327 terminal0, first16 resource/nativeexact gate then symmetric6arm192WG FFN GPUtimestamps,512graphs/arm, fullrawG/U/GLU/down/Q8bytes nativeexact: parent0.3235ms, WG8-only0.4630ms (+43.12%), sharedruntimeflagfalse0.4755ms (+46.99%). This comparison was later found confounded: WG8 also replaced the fixed two-row call with a runtime row count; it does not isolate scheduling cost. Conditional upcode adds~2.70%relative WG8-only in that implementation. Source factors can affect compiler allocation/scheduling, so do not claim a single s_barrier instruction accounts for entirecost. NoGPUcrashes; ownjobs terminal, waiter resumed.

Next implementation must preserve original independent subgroup dynamic loop for ordinaryQ3, including existing chunk2 behavior. Common wrapper can branch only for task acquisition: ordinary uses original per-subgroup nxt/lim and broadcast; paired uses WG-uniform32rowclaim/sharedjob/barriers. Both flow into a common original compute call site, with epochcount1normal/4paired. WG barriers execute only under the uniform record-level pairedflag, so ordinary subgroups may exit independently without stranding a WG barrier. This uniformity needs source/SPIR-V proof. Keep conditional upaccumulation as one variant; alternative outer 1/2 phase loop reuses original Kbody without inner-loop flag, sacrificing Bregisterreuse. Measure both rather than assume code shrink wins. First<=16WG plus rowtails/bias/nativeexact andresource gates, then213recordmodelaudit, thenmatchedmicro/fullmodel. Current known-good parent remains preferred; original separate-body fusion remains exact but no establishedfull gain.


## Hybrid scheduling and fixed-row specialization correction

`build_hybrid_shader.py` generated `hybrid.comp`, original independent subgroup nxt/lim/chunk rules for ordinaryQ3, WG32 jobs only paired, one common compute call site. Main shader has an unconditional WGbarrier after every operator and gridbar markers contain WGbarriers, so all WG lanes enter the same record. Pairedflag is loaded from readonly tape at identical base+58; therefore WGuniform at record entry. Only paired path executes WGjob/packingbarriers; ordinary subgroup loops can terminate independently and rejoin main's record barrier. Preserve this main barrier invariant.

Build91093 terminal0. Batch21624 terminal0:16WG first nativeexact/F32/Q8/resource tests,26tailcases and8biascontrols, then192WG fullmodel off/fused×2prompts all213logits/hidden records/tokens/acceptance exact. Microparent0.3255ms/off0.4750/fused0.4785(+47.00%vsparent); restoring subgroup schedule did not materially fix regression. Full throughput skipped by explicit>5%micro regression gate (correctness already checked). Original waiter resumed.

Source review found the crucial confound: shared/hybrid/WG8 wrappers call compute(first,min(2,rows-first)) for everyrow. Parent calls compute(first,2) in a full-row fast branch, with dynamic count only for tails. Losing the constant bound can prevent unrolling/specialization and introduce indexed accumulator/control overhead. This is a hypothesis until the new control completes; earlier43%attribution to WGjobs alone was too strong and is superseded.

`build_fastpath_controls.py` restores parent-style constant2 fast branch in both `hybrid_fast.comp` and `wg8_fast.comp`. Build24046 terminal0, both validated SPIR-V. Fastpath batch30685 is in progress (check authoritative session): first16/tails/biases; then matchedparent/WG8fast/hybridfast-unfused control, fullmodel correctness, micro and conditionalfullthroughput. Dedicated `hybrid-fast-results` and `fastpath-control` prevent clobbering old evidence. No adoption or gain claim yet.


## Fast-path controls overturn scheduler attribution; phase prototype

Fast batch30685 terminal0, original waiter resumed. `fastpath-control/*/summary.json`: parent0.3245ms, WG8-only withconstant2restored0.3230ms (-0.46%, withinnoise), hybridconstant2withruntimepair code0.3725ms (+14.79%). Thus the previous43%comparison DID NOT isolate WG scheduling: losing fixed-row specialization was the major source-level confound. Scheduler-only withfastrow bound shows no material penalty in this workload. Update all future explanations accordingly. Conditional fused body/compiler layout remains costly; no claim one branchinstruction accounts forall.

Hybridfast resources96VGPR/38SGPRspills/16KiBLDS/0scratch butcode462756bytes (+8.64%vsparent). All26tailcases,8biascontrolrows,4patternpackedtests andfullmodeloff/fused×2prompts nativeexact. Its6armmicroparent0.3270/off0.3740/fused0.4085ms (+24.92%vsparent,+9.22%vsoff). Fullthroughput correctlyskipped by>5%microregression gate. No adoption.

`build_phase_shader.py`: one/two outer matrix phases, original unchanged op33 K-loop, optionalfusionlogic onlyafter reduction. Preserves original subgroup jobs ordinary/WG32paired andconstant2fastpath. No packedBregisterreuse acrossphases. Savedgate4privatefloats forleader. Compile83859 terminal0. GPUfirst72498 terminal0 at16WGs: fourpatternsrawG/U/GLU/downandQ8nativeexact; resources120VGPR/38SGPRspills/16KiBLDS/0scratch,code427344 (+0.324%vsparent). Do not launch at192: no residencyheadroom established for120VGPR. Only16tested. Thisis an unpromoted testvariant.

`build_phase_lds_shader.py` / `phase_lds.comp`: move savedgatevalues to existing mega_lds_float[0..63], same indexlater overwrittenbyGLU. Eachwaveleader writes itsown gateentries atphase0 andreads thesame entries atphase1; no cross-invocation handoff betweenphases, no additionalWGbarrier required there. Allwaveswrite disjoint rows/columns; interepoch indices disjoint, nexttile cannotreuse until existing finalWGbarrier; packreads otherleaders onlyafter existing WGbarrier. NoextraLDSallocation. Compile42257 terminal0, Vulkan1.2validationpassed. First16job29284 is live atwriting (checkauthoritative session). No resource/performance claim forLDSvariant untilresult. Next if96VGPR/16KB/0scratch andexact, runtails/bias/full213recordaudits andmatchedmicro/fullbench. Ifstill120, do notreuse192grid; reducepressure further or derive capacity conservativelybeforelargerprobe.


## Phase LDS outcome; pivot back to Q3 arithmetic

Phase-LDS first29284 terminal0: native/parent/fused rawG/U/GLU/down/Q8all exact,96VGPR/38SGPRspills/16KiBLDS/0scratch,code429156bytes (+0.749%vsparent). Thus shared scratch successfully removed120VGPRpressure of private gatearray. This does not establish speed.

Batch44100 terminal0, waiter resumed. All26tail/shape cases,8biascontrolrows (4in-place inputs×0/1/2biases each), full213logits/hidden records peroff/fusedmode across2prompts exact; alltokens/acceptance same. Microparent0.3280ms/off0.3320/fused0.3460 (+5.488%vsparent,+4.217%vsoff), parentreplicate drift~1.85%; no gain. Fullthroughput skipped at>5%microregression gate. NoGPUcrashes and no adoptedcandidate. All ownjobs terminal atthisentry.

The scheduler-only attribution was wrong: fixed-row control parent0.3245ms/WG8fast0.3230ms shows no material cost to WG8 in that workload. Losing fixed-row specialization explains a major source-level regression; preserving constant rows and keeping optional logic out of the K-loop are necessary design constraints, but neither alone made fusion faster. Avoid repeating these rejected fusion rewrites without a materially new lead.

Next useful independent lead: port existing exact Q3 integer shared-activation-bias optimization from `isolated/q3-shared-bias/build_shader.py` (C1 op27) to current MTP C2 op33, first retaining original two-row fastpath, subgroup scheduler, and allotheroperators. Repack0..7 directly and move -4*sum(Bq8) once perK/j into q_sum; reuse correction acrossrows. Existing scalar/random proof bounds partialsum safelyint32 and unchanged finalintegerdot means original F32scale/reduction order retained. Then evaluate fourrows independently (arrays[2][4], literal4fastbranch, adjustvirtualWgn.x/firstrow4 withtail/batchcoverageproof), factorial sharedbias×row4. Historical~6.13%local improvement was C1 bias+fourrow, not evidence for C2/MTP. Keep FA unified, parentmath/referencecontrol,<=16physicalWGs,96VGPR/16KiB/0scratch gate andfull213record audits beforemeaningfullargerbench. Do not blindly compose rejectedfusers.
