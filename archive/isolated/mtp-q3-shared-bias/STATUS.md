# MTP Q3 C2 shared-bias / four-row factorial

All work private; parent reference is `isolated/mk/gen/operator_only_mtp_all_f32.comp`. All42opcodes/FA retained. No production or installed changes, no adoptedcandidate, globalgoal active.

## Changes and proofs

`build.py` / `bias2.comp` ports earlier C1 exactintegerrecentring to op33C2: decode weight0..7 directly; onceperK/j compute -4*sum(16signedQ8values), reuse across existing2outputrows. Original F32scale/reduction, scheduler andconstant2fastpath unchanged. `integer-proof.json`:2048scalarcases,100000randomdots,int32absoluteintermediatebound22528.

`build_rows4.py` produces independent rows4(nointegerchange) andbias4(both): [2][4]accumulators, constant4full-rowbranch,1..3rowtail, virtualwgn.x=ceil(oldX/2), firstrowstride4. SameindependentSGscheduler/chunkrules. `row-coverage-proof.json`:4ceil(x/2)>=2x checkedx0..65535; linearrowcoverage in x+newX*z andsameybatch; stride_d guardsextra groups. Not a proof of arbitraryhardwareforwardprogress.

Build98384(two-row) and3609(four-rowvariants) terminal0; pre/post SPIR-V Vulkan1.2 validationpassed. First16operator27349/tails/bias andbenchmark48897 terminal0. Four-rowfirst27065/quality47556/factorial87701 terminal0. Allguardsresumed originalquietwaiter. No newGPUcrashes.

## Correctness/resources

Eachvariant: first16WGs fourchangingin-place inputs, rawG/U/GLU/downandpackedQ8 byteexact.26tail/shape/native+independentsingle-column comparisons;8biascontrolrows across4shapes includingR4097, each4inputs×0/1/2biases, allnativeexact. Mode label`hybrid` in some inherited operatorlogs means candidate in that script; it does not mean fused arithmetic is enabled. No hostfusion orconsumerproof changes used here.

Eachvariant at192WGs: Roman114+Cpp99full-vocabulary logits/hiddenrecords, tokensandacceptance exact to qualifiedreference; no nativeops in final12graphs. `model/comparisons.json` andpervariant directories preserveevidence.

Allvariants96VGPR/38SGPRspills/16KiBLDS/0scratch. Codesizes: parent425964,bias2424684,rows4457260,bias4453036bytes. FirstGPUprobe<=16physicalgroups; largeronlyafterresourcegate.

## Performance: no full-model improvement

Two-rowfirstmatchedmicroparent0.3240/bias20.3215ms (-0.77%); full6armparent38.645/bias238.539/native44.3405t/s. Underload3–4externalcompilers,~29%CPU. Noestablishedgain.

Matched8armfactorialGPUtimestamps,512FFNgraphs/arm,allraw+packedbytesexact: parent0.3265ms,bias20.3220(-1.38%),rows40.3140(-3.83%),bias40.3155(-3.37%). Q3gate/up+Q4downstreamedweights; fourinputpatterns; no hostfusion. Localresultsarenot full-modelspeedups.

Matched10armoriginalasyncMTPthroughput: native44.6035,parent39.024,bias238.8455,rows438.476,bias438.662t/s. Candidatevsparent -0.457%,-1.404%,-0.928%. Drift(native,parent,bias2,rows4,bias4)=1.693%,0.808%,0.731%,1.905%,1.098%. All129tokens55accepted/74proposed identical. Externalcompilers3; noquiet/adoptionclaim. Combiningbiaswithfourrows didnot additively improve localorfullspeed.

## Next lead

Stopblindlyadding arithmetic/fusion variants whose localgains failfullmodel. A broaderoccupancy lead is documented in `isolated/occupancy-discovery-research/NOTES.md`, primaryOOPSLA2016paper. Sourceaudit shows raw gl_WorkGroupID/gl_NumWorkGroups appearonlyonce inparent main, so normalizedparticipatingIDs/countcould potentiallyfeed existingworkpartitionwrappers. No implementationorgridincreaseperformed. MustauditVulkan/RADVprogress+memorymodel assumptions andregistrationoverhead first; initialprotocol tests<=16WGs, andretainresidencyheadroom untilsoundqualification. Goal remainsfaster-than-native unifiedmega/FA; latestnative still~14.3%higher throughputthanparent.


Research checkpoint: primaryOOPSLA2016paper andcurrentVulkan memory-model appendix were opened during this turn. `isolated/occupancy-discovery-research/NOTES.md` now outlines a cap16/physical16 first experiment, explicitpad/arrival/dyn separation, normalized-ID audit and counterdiagnostics. No discoveryshader/CPUmodel/testAPI has been implemented, and no occupancyincrease has been run. AllprivateGPU/compilejobs fromthisturn areterminal. Nextavailableaction is logicaladmission model +exactpaperprotocol/spec audit, then cappedprivateprototype, not a larger fixedgrid.
