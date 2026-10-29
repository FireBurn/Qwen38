# Explicit padded-Q3 column reuse

864operatorchecks exact(native110,padded112,new112),scalaroracle/guards/inputimmutability,zeroGPUerrors. C2 instructions5556->4220,VMEM274->204,code30988->23444bytes;48VGPR/zeroLDS/scratch unchanged. C1 instructions2053->2064,VMEM100unchanged. Shader preserves original K/reduction/arithmeticorder;nohostchange. Shortmodel32 freshstock/frozen/reuse target38rows75055... exact,alltokens/counters. Broader5case numericalqualification running. No timing result or speedclaim yet.

All5cases now pass:630unique requestedtargetrows exact, including populatedKV2580..2644 and boundary174..302. Fixed24underload timing started; no result yet. Frozen primary control is unchanged.

Fixed24discovery complete:raw+1.5515%[-0.2004,+3.3341],only3/6matchedblocks,incremental_gain_supported=false. Matched effects+0.2443,+0.4943,+2.2772%;insufficientblocksnotqualified. CPUloadrose~100%;runqueue/buildmismatchrejectsblocks2,4,5 (zero-based). All513tokens/279drafts/234accepts exact,noGPUerrors. Do notrunindependentconfirmation(triggerfailed)orresample. Focused96armGPUtimestampdiagnostic nowrunning,separatequestion,notmodelproof.

Focusedmicro96arms complete,all8fullshapes/replicas/timedbytes exact,noGPUerrors. C2streamtimechange+0.749%[-4.472,+6.256]K5120,+1.134%[-5.800,+8.578]K17408;cachedC2intervalsalsocrosszero. No isolatedC2gainestablished.9sensorerrors/246processwidesamples;notstrictclockmatched. Fewerinstructionsarenotproof:frozen/reuseweightsamebytes,oldreloadsmayhitcaches,memorytraffic/latency/schedulinglikelylimit(inference,nocounters). Keepfrozen;noneedconfirmation. AllGPUjobs terminal12502/90168. Publishcompleteevidence,thennexttraffic-removingcandidateorlongKVprofile;notmoreinstructioncount-onlyvariants.
