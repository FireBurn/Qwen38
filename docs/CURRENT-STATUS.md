# Current work — 2026-10-30

**Latest confirmed result:** wider-argmax nativeconfiguration+2.3549%steady decoding versusstock[+1.5294%,+3.1871%],all12externally load-matched blocks in a fixed48-runindependentconfirmation. Full-generation confirmation+2.1680%[+1.3150%,+3.0282%]. Discovery separately+1.9201%[+0.7141%,+3.1405%],all12blocks. All120timedprocesses preserve exactnative513tokens/279drafts/234accepts, zeroGPUerrors; assets recheckedunchanged. About15.65GiBVRAMboth. [Implementation, source, build and full evidence](NATIVE-ARGMAX.md).

Five-arm combined-host correctness qualification passed: 530 raw target rows per mode matched native bits, tokens and counters, with intended feature activity verified. The predeclared fixed100 discovery completed. Combined versus stock was +3.399% [1.863%, 4.958%] across six matched blocks, but padding versus wide alone was inconclusive across four matched blocks (+2.476% [-0.520%, 5.562%]); the predeclared confirmation gate was not met. This is discovery evidence, not a confirmed combined gain. Widerargmax confirmation10091completed successfully; allcompleted timingdata are archived.

**Other confirmed configuration:** paddedQ3 atnativecap100+1.331%[+0.348%,+2.324%] in its independentfixed48test, about3GiBextraVRAM. [Separate proof and limits](NATIVE-DEFAULT-BASELINE.md). No head-to-head ranking or additive/combinedgain is established between these separate experiments.

## Next work

Compose widerargmax withQ3padding/native100in a NEWprivatehost, preserving bothqualifiedcomponents. The newcombinedhost buildswiththequalifiedQ3extendedcontext/matchingobjects andonlythetestedargmaxselectionblock. It passes630adversarialcases/1680indices perarm andfive-armshort38rawrows perarm,exactstocktokens/counters,noGPUerrors. Broader 530-raw-row-per-mode audits passed; the predeclared fixed100 stock/private/component/combined throughput comparison completed. No combinedgainyet. Prior gains must not be added.

A two-stagehierarchical reduction, output-head integration, mappedCPUfusionplanreuse andimmutableHadamardcorecache remain distinct follow-ups, not confirmedcombined gains. No fastermega kernel or productiondeployment established.

## What the preceding tests ruled out

- Restrictedbackendtemperature-only sampling withoutwiderargmax:fixed72primary+0.122%[-0.672%,+0.921%], no supportedstockgain; conditionalconfirmationnotrun. CPUtemperature-only regressed1.749%; backendoffloadrecoveredthatcontrol'sloss. [Completeevidence](NATIVE-GREEDY-SAMPLING.md).
- PaddedQ3/cap400combined lost1.69%versusnative-defaultstock. Cap400gains observedunderoldforced-nonmapped allocation didnottransfer tonativedefaults. RestoringmappedVRAM recovered~28%versusthatoldharness, butrestoresanexistingdefault. Originaldata/baselineflagsremainarchived.

## Widerargmax validation and recorded failures

Stock/privateoff/wideindices match on630adversarialcases/1680rows PERMODE, includingNaNs/infinities/ties/zeros/subnormals/shapeedges. ThreeQwenconfigs pass530fullrawtargetrows each,with backendscalaractivity and positivewidepipeline selection. Fixed24operatorgraphwalltime−60.9% isdistinctfromtheconfirmedmodelgain; wholeprocessloadmatching andintrusiveprofilelimits documented.

Firsthostbuild pointertypeerror and firstmicrotelemetryfailure are preserved. The microfailureoccurredafterone nativeprocess,beforeanycandidateprocess,becauseGPUclock/powersysfsreturnedEBUSYaroundnormalruntime suspension. Version2recordsoptionalGPUgapswhileCPU/build/runqueue remainrequired; no manualpowermanagement or failed-attemptpooling. Private historicalcachecleanup1.80GB preservedsource/SPIRV/binaries/logs/rawaudits/main timingcache. [Phasehistory](../archive/isolated/native-argmax-review/STATUS.md).

Onlyprivate review-workspace files arechanged; Claude/production/model/system configuration remainsuntouched. Completedresults, failedattempts, sources/provenance andunvalidatedleads arekept together. Activefuturetimingdata willremainwithheld untilterminal.

[Combinedphasehistory](../archive/isolated/native-pad-wide/STATUS.md), [smallcompositionpatch](../archive/isolated/native-pad-wide/host.patch), [five-armshortsummary](../archive/isolated/native-pad-wide/short-summary.json), [predeclaredfactorialplan](../archive/isolated/native-pad-wide/MODEL-TIMING-PLAN.md). Theplanrequiresbenefitoverstockandbothcomponentcontrols beforeconditionalconfirmation. ExactcompletedrawauditduplicateswerelinkedbyverifiedSHA256,reclaiming1.90GBwithoutdeletingpaths/content/evidence; see[deduprecord](../archive/isolated/native-pad-wide/audit-archive-dedup.json).

The combined comparison now requires evidence in every padded run that its qualified 78-entry weight cache actually existed and did not report a budget fallback. This pre-measurement protocol revision detects silent fallback; cache diagnostics may affect startup time. The original plan is preserved alongside the revision. The completed five-arm audit and its feature checks are archived in the qualification summary.

[Five-arm qualification summary](../archive/isolated/native-pad-wide/qualification-summary.json): all 2,650 mode-row checks passed with no new GPU errors. The completed timing dataset is archived.

[Combined factorial discovery](../archive/isolated/native-pad-wide/model-timing512/20261030T185248Z/confirmation-analysis.json) and [secondary outcomes](../archive/isolated/native-pad-wide/model-timing512/20261030T185248Z/outcomes-summary.json): all 100 processes preserved expected tokens and counters with no new GPU errors. Adding wider argmax to padding was +1.677% [1.210%, 2.146%] in four matched blocks; adding padding to wider argmax was inconclusive. The interaction had only two matched blocks. Background compile load changed substantially; all ten blocks, without the load matching, give combined vs stock +3.182% [-2.117%, 8.768%]. No independent combined confirmation was run because the predeclared incremental padding gate failed.
