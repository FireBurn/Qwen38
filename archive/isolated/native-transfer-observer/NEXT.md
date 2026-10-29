# Next actions

Pinned core/base provenance is reference-source.json; use commit aa8ab0504deda8ef55958aa2c7ccdee3eab924ca when making future private core changes, not a moving checkout.

Read STATUS.md, runs/20261029T205352Z/analysis.json and static-triage.json. Currentprofile/shaders/CPUplanning unchanged; all GPU jobs terminal. Source/timing evidence points to1850synchronous tensor-set queue submissions, not the earlier guessed2294inputs. Avoid assuming every tensor-set is a graph-input copy until names/flags are captured.

1. Extend only observer CPU records with copied tensor name/type/flags + requested size at sync setter, bounded CPU storage. No pointer retained aftertensorlifetime; snapshotnamesimmediately. Four fixed native profilegenerations aftertwowarmups, same reference tokens/counters, serialguard/copy2driver;no speedclaim.
2. Map actual tensor kinds back to original readonly .27core scheduler/graph inputs. Check sourceoverwrite/graphcopy/sourceCPUbuffer/destinationGPU events and completion guarantees. No Claude/production mutations.
3. If confirmed graph-input copies dominate, implement private opt-in immediate snapshot API (context-owned pinned staging, nativecopyrecording, stableinflightownership/fallback) and a private opaque scheduler TU or corehook to use it. Do notchange ABI across unmatchedTUs, replaycommands, skipbarriers or simplyremove sharedstagingwaits. Test caller sourceoverwriteimmediatelyaftercapture,inflightoverflow/recycling/multiplegraphs,destroyorder,2D/noncontiguous/unsupportedfallback,fullnumerical cases and GPUerrors before fixed A/B.
4. Preserve native-submit-budget candidate as experimental only: discovery4matched+.7534%primary butindependentconfirmation0matched, notconfirmed; no retry/extension/pooling. FewerbatchesmaytradeearlyGPUoverlapagainstdrivercost; prefix-preserving latebudget is only a hypothesis, lowerpriority than measured1850synchronoussets.

All work limited to megakernel-review. No desktop/system/clock/affinity changes. No faster mega kernel demonstrated; goal remains active.
