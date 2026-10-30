# Native mapped-VRAM state

All five full-target cases pass530rows/tokens/counters,noGPUerrors, same immutable qualified4e1381cdbackend and production.27/.7core. Only candidatechild unsets GGML_VK_DISABLE_HOST_VISIBLE_VIDMEM; sourcebuffer implementationprefersdevice-local+host-visible+coherent, not sysmemprefer.

Mapped CPUmetadata profile (native-transfer-observer/mapped-metadata-runs/20261030T003419Z) completedfourmeasured/sixnativegenerations129tokens/74drafts/55accepts. Exactsame17metadatarecords/1850syncsetrequests,zerooverflow. Queues4579->2137:syncset1850->0, fencewait518->222;graphqueues1767unchanged. Syncsetwallmean17.347msCPU17.272ms vspriorunmappedprofile643.613/91.145ms(nonmatched profiles,notTPSproof). Seeprofile-summary.json.

Fixed48discovery completedsession74921terminal0,model-timing512/20261030T005211Z. All48native513tokens/279drafts/234accepts,noGPUerrors. Eightof12external-loadmatchedblocks:primary+28.599084%[25.905216,31.350590]. All12raw+29.779504%[25.024623,34.715222]. Fullgenerationsecondary+28.342707%[25.601768,31.143460]. Matchedmeans31.669/40.617TPS,CPU89.876/89.827%,builds10.763/11.060,runqueue23.143/23.155,clock1683.813/2181.625MHz,power113.856/160.050W,VRAM~18.65GiBboth. Wholeconfiguration/NATURALDVFS+powertradeoff,notshader/equalclockproof.

Independentconfirmation36431completedterminal0: model-confirmation512/20261030T011412Z. All48expected513/279/234exact/noGPUerrors. Fiveof12matched:primary+28.305168%[22.369779,34.528447];all12raw+28.898817%[24.309577,33.657482];fullgenerationsecondary+27.986793%[21.928916,34.345647]. Matchedmeans28.992/36.999TPS,CPU91.516/91.386%,builds26.820/27.094,clock1679.85/1971.05MHz,power108.50/150.42W. Togetherwithdiscoverythisconfirmsold-harness-restorationeffect;no pooling. Seeconfirmed-harness-restoration-20261030.json. Default-stockcomparisonpending,originalqualifiedconfigunchanged/noproductiondeployment.

Protocolrevision24->48occurredBEFOREfirstmappedTPSmeasurement;v1plansandtiming-plan-revision.jsonpreserved. Notapostresulttestextension. Conditionalconfirmation48planalsopredateddiscovery. Activeconfirmationexcludedfrompublicationuntilterminal.

Baseline caveat:unsettingdisablerestoresanexistingnativeDEFAULTthattheharnessoverrides. Awinwouldbeagainstthepreviousconstrainedharness,notnewshadergainorproofagainstnormallyconfiguredstock. Needseparatedirectunmodifiedstock/defaultallocationcomparisonbeforeordinary-stockclaim/generalrecommendation. Priorcontrolledresultsvalidonlywithinthedocumentedruntimeenvironment;do notaddhistoricalpercentages.

CurrentGPUwork:directdefault72attributionsession84988;see../native-default-baseline/STATUS.md. Constantbroad34006/clear88900terminal0;all530rowsand6resets nativeexact. AllowncompilesterminalbeforeBARtiming. No overlappingGPUwork;allClaude/production/system/desktop/clocks/affinityuntouched. Keepcurrentqualifiedunmappedconfig untilcompleteevidence;goalfastermega notachieved.
