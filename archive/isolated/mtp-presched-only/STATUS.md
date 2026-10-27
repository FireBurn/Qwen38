# Private preallocation scheduling isolation

Source cloned from qualifiedprivate335d5698compiler,onlynew change AMD aco_ir.cpp debugalias nosched-pre=DEBUG_NO_SCHED. Existing nosched all3bits unchanged. No comments/commits/externalactions. Separate nice15/j2ThinLTO build and immutable driver bundle; allprevious sources/bundles intact. Driver SHA397f5e42d89c749f5275727008a166fdd85faaf6754421ed9843f9d8a2a714a3; SPIRVTools dependencyhash in driver/manifest.json,othersnotfullyfrozen.

First16WG5policy/resource probes allnative-bit-identical:4inputpatterns/0-2bias,64graphs,final16fullymega. Full-default reproduces oldprivateHash3326192224/code425004/96VGPR/9SGPRspills/16KiBLDS/0scratch. Full-pre96VGPR/16KiB. Nofa-default96VGPR/8SGPRspills/2KiB/0scratch,code382556; nofa-pre72VGPR/same8/2KiB/0,code386184; nofa-all72/same8/2KiB/0,code399244. Same-driverprescheduling nowisolated frompostRA ILP/VOPD.

Microbenchmark completed terminal0: sameFA-free8Q4/Q5 K5120/R17408/two-column streamed matrices,default192/pre192/pre256/reverse. Means0.8345/0.8195/0.8195ms. Apparent1.80%gain belowdefault5.04%drift, varyingclocks. Alloutputs byte-identical,pre256kept64spareofsource-derived320. No stablemicrogain.

FullMTP192/256 validation complete for2prompts,3modes(default192/pre192/pre256). Eachmode's213full logit/hidden records byte-identical toexistingreference, all66/65tokens and28/38,32/33acceptance identical. Last12graphs144nativeFA/reduce dispatches only.

Original async10-arm same-private-driver fulltiming completed: native45.3000t/s,unifiedmega39.8665,nofa-default39.6715,pre19236.4805,pre25637.6650. Pre256recovers3.247%vspre192, butremains5.522%slower thanunifiedmega and5.058%slower thannofa-default. Pre1928.493%slower thanunifiedmega. Control drift native0.887%,unified1.194%,nofa1.077%,pre1920.145%,pre2560.053%. All129tokens/55acceptedof74proposed identical. Threeexternalcompilerprocesses,CPU22.2-23.5%,clocks3080-3227MHz. No quietadoptionclaim. Thelegacyrelative_to_installed_mega_percent outputfield actuallymeans unifiedmega onthissameprivate397driver; numericvalues unchanged and an accuratelynamedalias addedto derivedsummary.

Decision: prescheduling-only disable notadopted. Regs72/greatercapacity do notoffset schedulingloss. Full-model gaininsidedeoptimizedfamily doesnotmean speedupagainstnormal/native. No furtheroptionalreruns ofthisknob. Driverbundle retainedasresearchdiagnostic, defaultoff. AllGPUchildren0,quietwaiter resumed, noinstalled/Claudechanges.

Next priority is larger actualoperator fusion, not more blanket scheduler switches: inspect existingBF16pair/GLUquant fusers and attemptsynthetic pairedQ5gate/up+SwiGLU+optionalexactQ8pack. Plan in ../mtp-fused-gate-up/PLAN.md. KeepFAunified and arithmetic/visibility intact; initial16WG,resourcegate,micro+fullmodelproof. CompactFA12KiB/querymicrotile possibilities remainunimplemented lowerpriority in NEXT.md.
