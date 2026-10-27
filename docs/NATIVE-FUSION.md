# Native SwiGLU → Q8 fusion: correctness diagnosis

The default-off native-backend prototype now passes the captured 32-requested-token model byte audit at **16 and 136 workgroups**, with and without the bounded-head path. Tokens and speculative counters match: 34 predicted, 19 drafted, 15 accepted. This qualifies the tested configuration only; no speedup is established.

## What failed and why

The first prototype compiled with unoptimized `glslangValidator` passed regular operator patterns but failed the model audit. The target diverged at the first audited verification: maximum absolute differences were about 0.05293 in logits and 0.05135 in hidden values. Identical generated tokens concealed these differences.

Changing vector buffer declarations to scalar loads did not change the failing model checksum. Retaining the original SwiGLU dispatch also failed. A diagnostic that retained native SwiGLU output and replaced only its quantizer produced the same failing checksum, localizing the issue to quantization.

Inspection of the actual native SPIR-V showed that its `glslc -O` build had transformed `d = amax / 127; inv = 1 / d` into multiplication by the rounded reciprocal constant for `d`, and `inv = 127 / amax`. The unoptimized prototype retained the divisions. Floating-point rounding makes those sequences observably different.

A targeted GPU regression uses a block maximum of `19.534229278564453` and an element of `3.4607887268066406`. With otherwise identical optimized controls, the old fused binary fails packed-output equality; the corrected build passes for both 17408 and 34816 elements. The checks retain this expected negative result rather than treating its nonzero exit as an unexplained crash.

Rebuilding the scalar-load fusion using native's `glslc -O --target-env=vulkan1.2 -fshader-stage=compute` settings restores the canonical model checksum:

`873abacccc270bc1a0669f62ac831dcc14ace252db9f60bbc0006a7c7b84dec2`

This is a compiler-pipeline consistency fix, not evidence that one rounding sequence is universally preferable.

## Evidence and scope

- [Threshold GPU regression](../archive/isolated/native-swiglu-q8/rounding-repro/checks.json): old binary fails packed equality; corrected binary passes both shapes.
- [Focused native-backend C1/C2 checks](../archive/isolated/native-swiglu-q8/operator-nativeopt16/checks.json): all floating SwiGLU and downstream Q4/Q5 outputs match over 64 pairs and four input patterns.
- [16-workgroup model comparison](../archive/isolated/native-swiglu-q8/model-nativeopt16/comparison.json) and [136-workgroup comparison](../archive/isolated/native-swiglu-q8/model-nativeopt136/comparison.json): complete captured target logits/hidden, draft candidate IDs/scores, tokens and counters match.
- [Standalone controls](../archive/isolated/native-swiglu-q8/nativeopt-timing/checks.json): twelve exact cases with buffer guards. All shader stages now use native's optimization settings.

The corrected fused pipeline has 48 VGPRs, zero spills, zero LDS, zero scratch, and 820 bytes of code on the tested private RADV/ACO driver. These are resource facts, not measured occupancy or throughput gains.

Only 14 target and one draft pair per eligible graph are fused by the conservative adjacent-node planner. Extending coverage needs graph/lifetime evidence. The native quantized-activation cache is retained; subsequent matrix consumers can reuse it.

A standalone GPU timestamp comparison is waiting for the unchanged quiet-load gates. The older waiter was stopped after verifying it was our own childless process because its compiler/control configuration had been superseded. Full-model performance against current production remains pending. No production or Claude worktree was changed.

See [Khronos shader layout guidance](https://docs.vulkan.org/guide/latest/shader_memory_layout.html) for the alignment hypothesis investigated along the way. It did not resolve the observed failure.
