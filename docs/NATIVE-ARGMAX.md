# Wider native argmax prototype

The256-lane prototype preserves native indices in630adversarialcases/1680rows perarm and passes all530Qwenrawtargetrows perarm, with exact stock tokens/counters and noGPUerrors. A fixed24operatorcomparison measures **60.899% less synchronous argmax-plus-gather graph wall time**, descriptive95% interval[56.951%,64.485%less], all6wholeprocessCPU/build/runqueue-matched blocks. **Full-model gain is unproven; a fixed72-run comparison is now running.**

## Implementation and correctness

Native argmax uses one subgroup-sized workgroup per row. The prototype uses256threads but retains the original lane-count specialization for finite tie ranking: bit-reversed original lane, then original index. AnyNaN triggers the original scan/tree comparison sequence. Input/output layouts, native operator API, device/context/header ABI remain unchanged. Opt-inR9700privatehost only; originalshader remains available.

Stock, privatehost/native andprivatehost/wide produce identical I32indices across15Kdimensions,1/2/5rows and14patterns: finiteunique/tied maxima, NaNpositions/allNaNs, infinities, signedzero, subnormals, dimensionedges. 630cases/1680rows PERMODE. Widepathselection is positivelylogged.

The modelcontrols arestockdefaultCPU sampling, private-nativeargmax withtargettemperature-onlybackend sampling, andprivate-wide withthesamebackendchain. Eachpasses530fullrawtargetrows across short/coding/math/populatedKV/boundarycases. Backendselectedtoken/scalararrayassertions and actualwidepipeline selectionpass, exactstocktokens/acceptancecounters, noGPUerrors. This is restrictedgreedyconfiguration qualification, notuniversalCPUchain tie/stateful equivalence. NoQ3padding/corecache/othernewkernel.

[Shader](../archive/isolated/native-argmax-review/argmax-wide.comp), [minimalhostpatch](../archive/isolated/native-argmax-review/wide-host.patch), [privatebuildrecipe](../archive/isolated/native-argmax-review/build_wide_host.py), [buildprovenance](../archive/isolated/native-argmax-review/wide-build.json), [adversarialcomparison](../archive/isolated/native-argmax-review/wide-checks/20261030T092907Z/comparison.json), [fullmodelqualification](../archive/isolated/native-argmax-review/wide-model-qualification.json).

## Measurements and limits

The native intrusiveGPUprofile recorded78ARGMAXcalls totalling41.9ms in the target timing table. It includes prompt/warmup, multipleargmaxshapes and serializesnodes/waits; no TPSforecast or purefull-vocabulary attribution. An inheritedstaticreport labelcap400waswrong; launchhadnooverride/native100, documentedin[metadatacorrection](../archive/isolated/native-argmax-review/gpu-profile32/20261030T091659Z/metadata-correction.json).

The isolated comparison usesK248320,16argmax+selectedvaluegather copies,60iterations and16warmgraphs,24freshprocesses in6alternatingABBA/BAABblocks. Sameprivatebackendbinary/client/driver; only opt-inshaderenvironment differs. Walltime includeshostsubmission/scheduling/waits, not standaloneGPUkernel duration. Natural clocks/power were observed, not matched. Whole-childCPU/build/runqueue matching does not establish benchmark-phase isolation, equal-clock efficiency, streamingperformance or modelTPS.

Firstmicroattempt stopped afterone nativeprocess becauseGPUclock/powersysfs returnedEBUSYaroundruntime-suspension, beforeanycandidateprocess. ItprovidednoA/Bcomparison. Itisretained; version2requiresCPU/build/runqueuetelemetryandrecordsoptionalGPUgaps withoutchangingpowermanagement. Freshfixed24data are separate and not pooled. Firsthostcompilepointertypeerror is also preserved and correctedbeforeGPUruns.

[Fixedoperatorprotocol](../archive/isolated/native-argmax-review/WIDE-MICRO-PLAN-v2.md), [operatoranalysis](../archive/isolated/native-argmax-review/wide-micro-v2/20261030T093239Z/analysis.json), [failedattemptrecord](../archive/isolated/native-argmax-review/wide-micro-attempt1.json), [phasehistory](../archive/isolated/native-argmax-review/STATUS.md).

## Full-model throughput test running

Fixed72fresh512-request-token processes,12symmetric6armblocks, all6permutations twice withorder+reverse. Primarywidebackend versusstockdefaultCPU; private-nativebackendcontrol separates shader contribution descriptively. Native100/mappeddefaults, originalstockcore/common/model/MTP1/q8KV/FA/ctx4096/privatecopy2driver. Originalnoninstrumentedsynchronizedrunner; audit/profilerOFF. Pair-specificCPU/build/runqueue matching, naturalclocks/power reported. No retries/extensions/quietgate/pooling. Onlypositiveprimarylowerbound with>=4matchedblocks triggers predeclaredindependent48confirmation. All513tokens/279drafts/234accepts must matchnative, stablepinnedlibraries/runtime and noGPUerrors.

[Fullmodelplan](../archive/isolated/native-argmax-review/MODEL-TIMING-PLAN.md), [timingrecipe](../archive/isolated/run_native_argmax_wide_timing.py). Active timing data are withheld untilterminal. No fastermega/equalclock/generaldeploymentclaim, noaddingindependentQ3gain tothisunmeasuredmodeleffect.
