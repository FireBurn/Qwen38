# RDNA4 instruction-prefetch opportunity

Primary ISA source: https://docs.amd.com/api/khub/documents/uQpkEvk3pv~kfAb2x~j4uw/content (RDNA4 guide, scalar prefetch section8.5 and SMEM instruction definitions). It defines instruction-cache prefetch via absolute or PC-relative addressing,128-byte cache lines and up to32lines. Prefetch acts asNOP when MODE.SCALAR_PREFETCH_EN is off. Mode enablement for our compute waves is not established.

Local private Mesa aco_opcodes.py922..923 defines s_prefetch_inst and s_prefetch_inst_pc_rel forGFX12. Targeted search of AMD compiler C++ and Vulkan C/H found no emitter/reference. This is a source inventory, not proof of executed machine-code absence on every pipeline. Installed LLVM23 IntrinsicsAMDGPU.td3228 defines llvm.amdgcn.s.prefetch.inst; this shows relevant compiler infrastructure but LLVMshaderbackend is disabled forourRADVbuild.

RADV already has radv_emit_shader_prefetch inradv_cmd_buffer.c3075, calling radv_cs_cp_dma_prefetch withshadercode_size. The latter inradv_cp_dma.c caps size below32KiB onGFX11+. This command-processor path is different fromwaveinstructioncacheprefetch; do not infer cache-miss elimination, cachelevel equivalence or a bug merely fromitscap.

Our qualified compiled shaders are about500KiB total, but total codebytes do not reveal executed working set or missrate. Kernel phase branches may use small hotloops and cold fetch costs mayamortize. Prefetch can waste bandwidth, evict useful lines or offer too little lead time. This is an independent proposed mechanism, not evidence that lowerVGPR counts failed because ofinstructioncache.

A future isolated experiment would first establish actualmodeenablement and hot-block instruction addresses; then add tightly scopedPCrelativeprefetch in a separate privateACO fork, preserveallnumeric/syncbehavior, audit finalbranch/PCrel relocation and padding, run <=16WG resource+micro+model gates, and compare quiet matrix/fullmodel timings against identical no-prefetch driver. Do not mutate currentlypinneddriver or assets. No driver/kernel/source mutation or GPUexperiment performed by this review.

Registerinventoryfollowup: gfx12.json13633 placesSCALAR_PREFETCH_EN atSQ_WAVE_MODEbit24. This locatesenablementbutdoesnotestablishcurrentdefaultorpermitignoringmodepreservation. No changeperformed.
