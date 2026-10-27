# Exact two-column GLU/Q8 host guard

CurrentMTPtrace has58adjacent descriptor-matching two-columnGLU/quantpairs withN34816,quantPC34816/136, plusone single-columnpair. LegacyguardonlymatchesN17408. NewhelperacceptsexactcapturedPCarrays forbothcases, derivesfloat/packedbytes andquantgrid fromverifiedN, retainsadjacency/range/overlap/flagguards. Flat contiguousindexmapping checked for52224elements. ExistingcombinedshaderalreadyusesquantPC.ne andneedsnochange; previouslyqualifiedSPIRV willbe reused byhash.

Sourceonly. Hostcompilation/current-helperCPUwitness/runtimeeligibility/GPUmodelchecks pending. NoGPUlaunched orcompilerstarted duringremainingperformance90113. Legacy392testdoesnotqualifynewtwo-columnguard. Prefixqualification was safelydeferredwhenwatcherhadalreadylaunchedtiming; that remainsseparate.


Update: private host build completed successfully. The exact current helper passed 767 captured-record cases with audit disabled and enabled. Shader SPIR-V remains identical to the already qualified 60-register fusion shader. Model16 off/fused GPU checks are queued behind the exact live prefix-claim guard process; no C2 GPU correctness or speed claim yet.
