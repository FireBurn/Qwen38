# Completed round and next work

Both GPU jobs terminal:fixed24model90168 and96armmicro12502. Modeldiscovery failed3/6matched (raw+1.55%[-0.20,+3.33]);confirmationtriggerfalse,do notrunprepare_confirmation orresample. MicrofindsnoC2gain despite24%fewerinstructions;C2streamtime+0.75%and+1.13%,intervalscrosszero. Nineprocesswidesensorerrors;no strictclockmatchedmicroclaim. Alloutputs630targetrows and864operatorchecks exact,noGPUerrors. Keepqualifiedfrozen400.

The evidence now pointsaway from merelyreducinginstructioncount. Originalreloadsmayhitcache,andweightbytesunchanged;memory/latency/schedulinglimit is inference,nocountersproof. Prefer memory-traffic/intermediate-stage removal or longKV profiling. Native110columnreusealone islowerpriority,notanautomaticnextcandidate.

Future design leads, not implemented:
1. Same explicitcolumnreuse on original110byteQ3 may offer a lowVRAM alternative. Existing columnreuse usespadded112 plus3GiBarena. Need separate sourceclosure/operator<=16WG/resources/modelqualification and primaryagainstqualifiedfrozen400; neither expected norclaimedfaster.
2. Bounded gate/up/GLU fusion: frozen Vulkan selection inspected around14830 supportsMUL_MAT+ADD but no matchingpairedMUL_MAT+MUL_MAT+GLUpatternfound. A C2wave currently holds2rows*2columns=4accumulators. Assigning those2rows to gate/up foroneoutputrow mightretain4accumulators,applyGLUafterreduction,andavoidtwointermediatewrites plusdispatches withoutmonolithicpersistentregisterpressure. This is a designhypothesis. It stillreadsallweights and mayloseconcurrency; do notclaimgain. Must proveidenticalGLUarithmetic,postreductionlayout,onlyeligiblecontiguoussameQ3weights/shareactivation/uniqueconsumers,noaliases/biases,strictDAGorderfallback. New descriptors/resourceownership/paddedcache need carefulprivatehostintegration. No unsafeinterWGbarriers orcommandreplay. See RESEARCH.md for CUDAinterleavedwriteback design, notadirectport ordecodeproof.
3. GPUprofiles are shortcontext; measurelongKV separatelybeforedeclaringattentionunimportant. KeepFA correctness and boundedpersistentlaunch rules intact.

No newcandidate above is selectedorimplemented. Currentcolumnreusecode doesnotfusepairmatmuls,changeMTPdepth or modifyClaude/frozenlibs.
