# Current work — 2026-10-30

**Latest confirmed result:** wider-argmax nativeconfiguration+2.3549%steady decoding versusstock[+1.5294%,+3.1871%],all12externally load-matched blocks in a fixed48-runindependentconfirmation. Full-generation confirmation+2.1680%[+1.3150%,+3.0282%]. Discovery separately+1.9201%[+0.7141%,+3.1405%],all12blocks. All120timedprocesses preserve exactnative513tokens/279drafts/234accepts, zeroGPUerrors; assets recheckedunchanged. About15.65GiBVRAMboth. [Implementation, source, build and full evidence](NATIVE-ARGMAX.md).

No ownGPUexperiment currentlyrunning. Confirmation10091completed successfully. Allcompleted timingdata are archived.

**Other confirmed configuration:** paddedQ3 atnativecap100+1.331%[+0.348%,+2.324%] in its independentfixed48test, about3GiBextraVRAM. [Separate proof and limits](NATIVE-DEFAULT-BASELINE.md). No head-to-head ranking or additive/combinedgain is established between these separate experiments.

## Next work

Compose widerargmax withQ3padding/native100in a NEWprivatehost, preserving bothqualifiedcomponents. Fresh five-case530rawrow/modeaudits and nativecounter/activity checks must precede a separate predeclaredstock/component/combinedthroughput comparison. No composition has been tested yet. Prior gains must not be added.

A two-stagehierarchical reduction, output-head integration, mappedCPUfusionplanreuse andimmutableHadamardcorecache remain distinct follow-ups, not confirmedcombined gains. No fastermega kernel or productiondeployment established.

## What the preceding tests ruled out

- Restrictedbackendtemperature-only sampling withoutwiderargmax:fixed72primary+0.122%[-0.672%,+0.921%], no supportedstockgain; conditionalconfirmationnotrun. CPUtemperature-only regressed1.749%; backendoffloadrecoveredthatcontrol'sloss. [Completeevidence](NATIVE-GREEDY-SAMPLING.md).
- PaddedQ3/cap400combined lost1.69%versusnative-defaultstock. Cap400gains observedunderoldforced-nonmapped allocation didnottransfer tonativedefaults. RestoringmappedVRAM recovered~28%versusthatoldharness, butrestoresanexistingdefault. Originaldata/baselineflagsremainarchived.

## Widerargmax validation and recorded failures

Stock/privateoff/wideindices match on630adversarialcases/1680rows PERMODE, includingNaNs/infinities/ties/zeros/subnormals/shapeedges. ThreeQwenconfigs pass530fullrawtargetrows each,with backendscalaractivity and positivewidepipeline selection. Fixed24operatorgraphwalltime−60.9% isdistinctfromtheconfirmedmodelgain; wholeprocessloadmatching andintrusiveprofilelimits documented.

Firsthostbuild pointertypeerror and firstmicrotelemetryfailure are preserved. The microfailureoccurredafterone nativeprocess,beforeanycandidateprocess,becauseGPUclock/powersysfsreturnedEBUSYaroundnormalruntime suspension. Version2recordsoptionalGPUgapswhileCPU/build/runqueue remainrequired; no manualpowermanagement or failed-attemptpooling. Private historicalcachecleanup1.80GB preservedsource/SPIRV/binaries/logs/rawaudits/main timingcache. [Phasehistory](../archive/isolated/native-argmax-review/STATUS.md).

Onlyprivate review-workspace files arechanged; Claude/production/model/system configuration remainsuntouched. Completedresults, failedattempts, sources/provenance andunvalidatedleads arekept together. Activefuturetimingdata willremainwithheld untilterminal.
