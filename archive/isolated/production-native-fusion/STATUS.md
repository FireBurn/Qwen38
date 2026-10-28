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
