# Compute outlining feasibility review

The binary audit in `function-inlining-audit.json` counts instructions directly from the SPIR-V stream: unoptimized and aliased modules each have 295 functions and 525 calls; optimized has one function, zero calls. Optimized bytes increase from 787660 to 1642904. SPIR-V byte size is not machine instruction-cache footprint. Static control-barrier sites increase from 57 to 142; this is duplication during inlining, not evidence of extra dynamic barriers.

Local private Mesa `src/amd/vulkan/radv_shader.c:576` calls `nir_inline_functions`, then removes non-cooperative-matrix entrypoints. `nir_functions.c:36` forces functions containing barrier intrinsics to inline; larger ordinary functions can survive the heuristic, but that does not establish a working generic compute call pipeline. The two local `radv_nir_lower_call_abi` pipeline invocations are in ray tracing, at `radv_pipeline_rt.c:479,1078`.

Official documentation https://docs.mesa3d.org/drivers/amd/function-calls.html confirms ACO call support and possible compute use, with register preservation and scratch-stack handling. This is infrastructure, not a ready compute toggle. Merely removing offline inlining is not a demonstrated optimization and can produce unsupported call IR in the existing compute pipeline.

Next action: retain the qualified shader while its performance comparison runs. If time remains dominated by matrices after the 60-VGPR comparison, inspect repeated machine-code regions and quantify hot-path instruction count before attempting source-level sharing or custom compute ABI work. Any call experiment must retain all opcodes, use a separate private build, gate compiler scratch/register resources at <=16 workgroups, and pass native micro/full-model output comparisons before larger grids. No candidate performance result follows from code size alone.

No pinned performance assets, driver source, or shader binary changed by this review.
