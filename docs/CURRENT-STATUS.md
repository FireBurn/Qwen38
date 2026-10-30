# Current work — 2026-10-30

**Now running:** fixed72matched-load target sampling comparison, guardedsession91245. DefaultCPU chain versusCPUtemperature-only versusbackendtemperature-only. Allthree configurations already pass530rawtargetrows each (1,590checks), with exact stock tokens/counters and zero new GPU errors. Backend mode returns sampledtokens/scalararrays on all530rows. The timed runner is the original noninstrumented binary, with no callback/profiler/activity logging. No sampling speed result yet. [Full protocol and numerical/activity evidence](NATIVE-GREEDY-SAMPLING.md).

**Latest confirmed gain:** paddedQ3 at nativecap100 independently confirms+1.331% steadyTPS[+0.348%,+2.324%],11/12load-matched blocks in a fixed48confirmation. Discovery separately+1.863%[+1.016%,+2.717%]. Full-generation confirmation+1.421%. All96processes exacttokens/counters, zeroGPUerrors; about3GiBextraVRAM. [Results, scope, power/load tables and archive](NATIVE-DEFAULT-BASELINE.md). These are separate configurations; effects are not added or pooled.

**Baseline correction:** cap400combinedQ3 lost1.69% versusnative-defaultstock. Restoring native mappedVRAM improved the earlier constrained harness by~28%, but restores an existing default. Older positive results remain archived with their actual flags. No fastermega kernel, equalclock efficiency or production deployment has been established.

## Next experiments

- Finish the fixed72sampling run without retries/extensions/pooling/quiet gates. Only a qualifiedpositive primary triggers the predeclared independent48confirmation. Owncompile and otherGPUwork remain deferred while timing runs.
- Nativeargmax currently uses one subgroup-sized workgroup per vocabulary row. A hierarchical reduction is a source-level hypothesis, not an implemented or measured shader. [Tie-order and validation requirements](../archive/isolated/native-greedy-sampling/ARGMAX-TRIAGE.md), [88,560CPU source-model checks](../archive/isolated/native-greedy-sampling/argmax-tie-order-check.json). Correctfinite tie rank usesbit-reversedlaneorder; the earlier lowest-lane inference was corrected before implementation. Nonfinite/GPU validation remains open.
- [Mapped CPU fusion-plan reuse preparation](../archive/isolated/native-mapped-plan-reuse/PLAN.md) remains deferred, with generated wrappers but no new mapped-path runs/gain. The separate immutable rotation cache passes numerical/clear checks but has no timed model gain.

The raw callback audit runner now reproduces all530originalstock target-logit rows before backend-sampling use. [Qualification](../archive/isolated/native-greedy-sampling/callback-qualification-summary.json). It is correctness-only because it adds synchronization and raw copies.

Private disk cleanup removed1.80GBof reproducible historical Mesa/RADV caches after one preflight disk-space stop before inference. Source, pinnedSPIRV, binaries, logs, raw numerical evidence and main timingcache remain. [Detailed phase history](../archive/isolated/native-greedy-sampling/STATUS.md).

Only private review-workspace files are changed; Claude/production/model/system configuration is untouched. Completed results, failed attempts, source/provenance and explicitly unvalidated leads are archived together. Unfinished timing data are withheld until terminal.
