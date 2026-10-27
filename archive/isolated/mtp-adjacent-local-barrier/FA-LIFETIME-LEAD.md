# Next structural lead: FA scratch lifetimes

Unimplemented analysis of native_order.comp. This does not establish a speedup or authorize a larger persistent grid.

The unified shader reserves Q/V8448bytes, score4096bytes, probabilities3072bytes and persistent slope/IQ extras. Scores start8448; probabilities12544. Score values are no longer needed after every invocation converts its assigned four values to rounded F16 probabilities (around3330-3370). A register-held probability stage, then a workgroup barrier, could allow probabilities to overwrite score storage. An in-place overwrite without that read-completion barrier is unsafe: another invocation may still be reading scores.

Aliasing probabilities alone is insufficient to reach12KiB: persistent slope/IQ data after score end still put the high-water mark above12288. Frozen Mesa ac_shader_util.h353 uses1024-byte LDS allocation granularity on gfx1201, so a12672byte logical region rounds to13312; five such allocations do not fit64KiB. Do not infer a capacity cliff from unrounded bytes.

Q stride isHSK_pad/4+2 (66f16vec4), requiring8448bytes for16 query rows. Removing the two padding vectors saves256bytes but may worsen bank conflicts. With a dense8192-byte Q region and a4096-byte score region, there is no room for persistent slopes outside those regions at12KiB.

Possible lifetime redesign: store mask-reduction flags in score storage before score production, and initialize16 ALiBi slopes into the Q region after all cooperative Q loads finish but before score masking. Slopes are no longer needed once probabilities are materialized, before the V-stage overwrites Q/V. This moves slope initialization into each KV tile and adds work/barriers; it may lose performance. The IQ lookup table can in principle use the existing constant table instead of shared memory, but actual captured FA variants are Q8 and should dead-eliminate IQ branches; this must be verified in optimized IR/resource stats.

Any experiment must keep integrated FA and native RMS, start<=16groups, preserve mask/causal/MQ/split-K tests and full native mid-state oracle. A12KiB layout still does not permit256groups with64spare while VGPR allocation stays96: the independent register bound remains256groups. Both resources must cross the existing proved threshold (e.g.72VGPR and<=12KiB) before320-capacity reasoning applies. Prior noFA/nosched controls already showed allocation reductions alone are not a performance win.
