# Production .27 SwiGLU/Q8 fusion and all-three combination

Captured32requested-token target-logit audit passes for native,fusiononly,allthree. No speed claim, production deployment or longcontext qualification.

## Port and lifecycle

Own source derives from production-native-shaders/host with preserved productionHEADaa8ab0504. Customfusion context fields are added only in the private ggml-vulkan-types.h. Allthree hosttranslationunits(main,buffers,debug) are recompiled with thatsameprivateheader; original generatedshaderarrayobjects are reused unchanged. Originalsource/build inputs read/copied only andverifiedunchanged; Claude's files untouched. No cross-TUcontextlayout mismatch. build.py/build.log andhost/build.json/build-argv.json/input-pins.json preserveprovenance.

Nativefactory/cache/descriptor mechanisms retained. Existing shuffle64four-binding fusionpipeline, metadata-view planner(max8nodes),floatmaterialization,prealloc_ycacheinvalidations andnarrowconditionalbarriercoalescing ported from oldqualifiedhost. Planner uses theactualproduction ggml_vk_should_use_mmvq eligibility decision; no forceMMVQflag oractivationpolicyoverride. HardwaregatedR9700/subgroup64/shuffle/fullsupport. Allchanges off bydefault. Legacy/fastplanner equality check enabled duringqualification.

Custompipeline isdestroyed/reset only after ggml_vk_cleanup synchronizes anddestroys pendingwork/descriptorresources. This avoids destroying a still-in-use pipeline. Device all_pipelines holdsweakreferences, soresetprevents laterduplicate destruction. Tests exercise normalprocess/context shutdown withoutnewdriverfaults.

## Operators and eligibility

Twelvearms pass: Q3-first andQ4-first consumerorders, eachC1/C2×native/fusion/allthree.64SwiGLUpairs,fourpatterns,Q3_K/Q4_K/Q5_K/Q4_0consumers,3outputrows.16physicalfusionworkgroups perdispatch. Alloutputs match ownnativebytes; fast/legacyplans identical; fusedpipeline24VGPR/zeroLDS/scratch.

Q4-firstC1 is theimportantnegativecase: productionRDNA4chooses thefloatpath forQ4_K singlecolumns. Fusion correctly staysdisabled (zeroactualfusedcalls), andallthree stillmatchesnative. Q4-firstC2 andQ3-firstC1/C2 allproduce64fusedcalls pergraph. No newtargetdrivererrors. Warmupcounts differ; rawus_per_graph isunqualifiedtiming andnotreported asgain.

## Production model target-logit audit

Three32requested-token arms(native,fusiononly,allthree) use common .27/.7stockcore/common,private7kdriver,copy2,SDMAoff,stockactivationpolicy and16fusionworkgroups. Actualfulltargetlogitcapturematches preservedunmodifiedproductionreference: SHA75055a49a5844ad14030f45cb76c11de20a44a6bb0e2db7c1c89a616137eb576,37745416bytes,38fullvocabrows across20targetbatches.34tokenIDs/19drafted/15accepted identical. Eachfusionarm records1159fusedcalls and1159conditionalcoalesces;61graphplanner equalitychecks. No unconsumed deferredGLU remains atgraphend. No newtargetdriverfaults.

Thisrecordsrequestedtargetlogits,not targethidden/internaldraftscorebits. model32/checks.json/comparison.json authoritative; oneverifiedlosslessgzipauditretains identicalrawcaptures. Does not prove timing or longcontext behavior. Quantizer/Q3actualdispatchsubstitution qualifiedseparatelyonproduction-native-shaders;thisrelease-stylefusionhostdoesnotadd atomicdispatchcounts.

Next: larger136fusiongrid targetaudit, two128-tokenprompts, production8maskfactorial andmatchedquiet512timing withunmodifiedstock/control. Existingnonfusionproductiontimingqueue remainsliveandunchanged. No performance result yet; CPUquietgate remainsblockedbyhighdesktopload. Current-systemdriver/library deployment separate.

## Larger grid, production factorial and longer captured prompts

model136-factorial/ all8masks pass32requested-token audit at136fusioncap: same38targetlogitrows/20batches,canonicalSHA75055a49a5844ad14030f45cb76c11de20a44a6bb0e2db7c1c89a616137eb576,34tokens/19drafted/15accepted. All4fusion-enabledmasks record1159fusedcalls/coalesces,all4disabledmaskszero;61fast/legacyplannercomparisons perarm. Allnewdriverchecks passed.

prompts128/ sixproductionarms pass: coding/math×native/fusiononly/allthree,136fusioncap. Coding136requestedtargetlogitrows across69batches,135088816capturedbytes,SHA d57c28c4140917e228a584ff8f7f2185caa0c08d51942a70b1dedf891cd95c27,130predicted/68drafted/62accepted;4001fusedcalls/coalesces whenenabled. Math138rows/70batches,137075416bytes,SHA cb052233cb56e8fe19113ff905700115393b19bfa263679d308ac800ca4a27f1,129predicted/69drafted/60accepted;4059fusedcalls/coalesces. Alltargetlogitbytes/tokens/counters equal ownsame-stacknativecontrol, allnewdriverchecks pass. Canonicalaudit compressed/hashverifiedbeforeunlinking eachidenticalrawarm, boundingdiskusage. These are128generatedtokens,not a populatedlongKVcontext stress.

## Uninstrumented timing-executable correctness and full queue

timing-smoke32/ all9arms(stock+8masks) match audited34tokens/19drafted/15accepted withtheoriginal .27timingrunner, no validationcounter/logitgetter/plannerdiagnostics. Warm/steady markers valid, exactmappedcore/common/backend/drivercheckedbyrunner. No newdriverfaults. Rawtimesunqualified underdesktopload andexplicitlyexcludedfromspeedsummary.

run_production_native_fusion_full512.py prepares18matched512requested-tokenarms(stock+8masks forward/reverse),samehostforallmasks,stockactivationpolicy,136fusioncap,no privatehead. Reportsrelativeperformanceagainstbothprivatecontrolmask0andunmodifiedstock; noadditivegainassumption. test_production_native_fusion_telemetry.py exercises actualmonitor/validityAST,errorcases pass. No timingstarted.

run_production_native_fusion_performance_after_shaders.py livequeuedbehind exactproductionshaderqueuePID1228109/start_ticks7139995,requiresitsworkflow-complete.json. InitialownPID1230556, originalsession60191; verifyactual/procidentitybeforeactions. Parentselectionexcludesexplicitlycancelled-before-launchrecords. Pinscurrenthost,allshaders,stockcore/common/backend,privateMesa,runner andqualification/smoke/monitorresults. Outputperformance/<timestamp>, futurepaired512/<timestamp>. Existingqueues untouched.

Mainremainingdecision isperformance. Avoidblindlyaddingmoreuntimedvariants whilethisqualifiedcandidatequeueawaitsCPUquiet. No faster-than-base result exists yet. BroaderKVcontext/hidden/draftscorechecks remain necessarybeforegeneraladoption; current-systemdeployment isnotqualified.

## User-authorized under-load A/B completed

User explicitly authorized continuing despite workload and matched A/B testing. Separate run_production_native_fusion_under_load.py bypasses CPU/buildquiet wait only; allmodel,driver,sensormonitor andGPUcompetition checks retained. Originalquietqueue scripts/pins untouched,ownchildlessquietwaiter paused/resumed.

Discovery18arms(stock+8masks forward/reverse),512requestedtokens/arm atunder-load512/20261028T171725Z. Meanstock39.0026t/s,privatecontrol39.4591,quantizer39.1155,Q3only39.2772,both39.2032,fusion38.9342,quantizer+fusion39.1219,Q3+fusion38.6004,allthree39.1668. Exploratoryonly:stockreturnCPUload59.3%vs50.9%initial;enabledmasksneverbeatprivatecontrolmean. Apparentstockgainsnotshaderattribution.

Independentconfirmationunder-load-confirmation512/20261028T172500Z:stock,allthree(mask7),bestdiscoveryenabledcandidateQ3only(mask2). Fixedprotocolrecordedbeforediscoverycompletion;18freshprocessruns,sixpermodes in3symmetric6armblocks,LatinrotatedABC/CBA blocks. Nooptionalstopping. Same513generatedtokenIDs,279drafted/234accepted inall36runs. Zero timed sensorerrors/monitorfailures/newtargetdrivererrors.

Confirmationstockmean38.4530t/s,allthree38.4797,Q3only38.4181. Pairedblockgeometric effects:allthree+0.0670%,descriptive95%tinterval[-1.7945%,+1.9638%];Q3only-0.0940%,interval[-1.7947%,+1.6360%]. All3blocksmatchpredefinedmode-meancomparabilitylimits(5ppCPU,3%GPUclock,2backgroundbuildprocesses);CPUloadandclocksstillvarybetweenindividualarms. Neithergainconfirmed. Intervalsuse3blockcontrasts/df2,limitedsampleandpossibletemporalcorrelation;notquiet/general-performanceproof.

SupplementaryindependentCPUobserverbeganduringconfirmation,limitedcoverage;desktopCPUroughly49%oflogicalCPUcapacitythroughobservedarms. Notusedtoprimaryconfidence/gating. Reportscompleteperarmtelemetryandprotocol;under-load-results-summary.json anchorsactualmeasuredconclusion. Backgroundloadcausesnoise,butbalancedblocksdoenabletesting:thedatahereareconsistentwithnoeffect,notwithaconfirmedcombinedwin.

Likelylimitation: register/instructionreductionsdidnotincreaseobservedreportedwavecapacity,anddominantmatrixweighttraffic/formatsareunchanged. Thisisamechanisticinference,notameasuredmemorybandwidthprofile. Furtherprofiling/targetedhostredundancyauditpreferabletoblindlycombiningmoreALUtweaks. No adoption orfastermega claim.
