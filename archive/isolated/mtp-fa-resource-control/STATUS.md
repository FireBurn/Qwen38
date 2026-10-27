# FA reachability and register/occupancy diagnostics

No installed-driver or Claude modifications. All shaders are separate parent-derived controls. Unified FA remains desired endpoint.

## FA removed from dispatch reachability

Switch/metadata omit FA22/MQ36/reduce23; optimizer drops unused functions/storage.16WG first5shape tests,4in-place input patterns,0/1/2bias outputs: allnativebyteexact. Resource96VGPR/8SGPRspills/2048LDS/0scratch,code382556 versusparent96/38/16384/0/code425964. PreSchedVGPR66 versus94. Shared-layout aliases otherwise unchanged.

192WG eight-matrix Q4/Q5 K5120/R17408/two-cols microcontrol parent/noFA/noFA/parent:0.840/0.835ms means, apparent0.595%below4.88/5.16%drift. Different clocks. No useful microgain.

Full MTP64requested two-prompt audit:213full logit/hidden records, alltokens and acceptancebyteexact. Last12graphs144nativeops, exclusively72FA and72reduce; remaining ops staymega. NativeFAfallback changes segmentation and compiledcode, so not a single-factor LDS experiment.

Six-arm original MTP128requested/129emitted: native44.6145t/s,parent38.933,noFA39.0495; apparent+0.299%below1.25/1.32%drift. All129tokens and55/74acceptance identical. No adoption.

## Compiler-scheduling and joint occupancy threshold

Frozen-driver ACO_DEBUG=nosched disables PRE_RA,ILP,VOPD scheduling together (aco_ir.cpp35), not just preRA. First16WG full/noFA probes native-bit-exact and validatorclean. Full remains96VGPR/16KiBLDS/38SGPRspill; noFA drops72VGPR/2KiBLDS/8SGPRspill,0scratch. No source/driver binary changes to obtain these probes.

Read-only frozen-driver RADV_DEBUG=info hardware query:64CUs,2SIMDs/CU,768physicalwave64VGPR/SIMD,12VGPRgranularity,16maxwaves/SIMD,64KiBLDS/CU. Source-derived conservative residency in occupancy-audit.json includes CU/WGP alternatives,256threads=4wave64/WG.96VGPR with16KiB or2KiB both256groups.72VGPR+16KiB remains256;72VGPR+<=12KiB permits320. Thus changing only either resource can fail to cross the occupancy threshold. This is a resource/capacity finding, not a performance win or proof of physical scheduling. Unknown shader first16 and64-group spare preserved.

72VGPR/2KiB control tested at192and256groups;256keeps64spare of320. Six-arm matrix micro scheduled192/nosched192/nosched256/reverse:0.835/0.8535/0.8425ms. Higher grid recovers1.29%within nosched, but scheduled control drift4.91%, and nosched remains slower. Alloutputs byte-identical.

Nosched full MTP at192/256, bothprompts: each213full binaryrecords and alltokens/acceptanceexact, last12graphs144FA/reduce fallbacks only. Original async10-arm modeltiming: native44.757,parent38.8885,noFA38.932,nosched19232.537,nosched25634.166t/s. Higher grid recovers5.0066%vsnosched192 (own drift0.288/0.152%), but still12.14%slower thanparent. Same129tokens/55acceptedof74proposed in all10runs. Threebackgroundcompilerprocesses throughout; generationclocks3085-3274MHz. Under-load diagnostic, not quiet adoption. Allscheduleroff harms performance despite better allocation.

Decision: noFA/nosched are diagnostic controls, not adopted. Lower allocation alone is insufficient. Next isolate prescheduling from postRA ILP/VOPD. Existing nosched flag combines all3; current parse_debug_string supports name ORing, not numerical/subtractive flags. Small private AMD-only debug alias nosched-pre=DEBUG_NO_SCHED could isolate the preRA pass while keeping the others. Separate source/build/frozen driver bundle and same-driver off/on required. Current otherqualified bundles must stayimmutable.

AllGPUchildren terminal0, numericalgates passed, original quietwaiter resumed. No modelqualitygeneralization beyond finitegreedy prompts/rollback paths exercised.
