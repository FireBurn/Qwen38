# Exact int4-weight / int8-activation dot products on R9700

The experiment uses two native 8-lane 4-bit dot products per eight weights:

`x_int8 = low_unsigned_nibble + 16 * high_signed_nibble`

Thus `dot(w_uint4, x_int8)` is the unsigned-low result plus 16 times the mixed-sign high result. Activation repacking is lossless. No approximation or change to the weight values is involved.

## Measured experiment

- Native system HIP runtime `/usr/lib64/libamdhip64.so`, system Clang 23, gfx1201.
- 1,048,576 output rows, 256 products each; 128 MiB of packed weights, group-major coalesced layout. Activation vector is shared across rows and repacked on CPU before timing.
- Both GPU variants match all 1,048,576 scalar CPU reference outputs exactly, including signed activations across the full int8 range.
- Ten alternating trials, 20 launches per timing event. Excluding first trial, median dot4: **237.288 us**; dot8: **236.120 us**. About **0.5%**, insufficient to establish a useful speed gain.
- Compiled VGPR counts: dot4 **36**, dot8 **13**; private segment/spills zero for both. Assembly explicitly contains `v_dot4_i32_iu8` and `v_dot8_i32_iu4` respectively.

The memory-bound microbenchmark establishes arithmetic correctness and a register reduction for this implementation. It does not establish an improvement in llama.cpp or the megakernel. Activation packing cost, real Q4_K byte/nibble order, per-block scales/min corrections, reduction, and Vulkan compiler support are not included. Current Q4_K storage pairs weights separated by 32 elements in each byte; activation packing must follow that layout, or weights must be losslessly repacked once on model load. Preserve Q3/Q5 consumers that share an activation vector.

## Reproduction

Run `sh build.sh`, then `./dot8_exact` with no alternate runtime paths. The ROCm SDK path in the build supplies HIP headers/device bitcode only; the executable links the installed native runtime. Raw timings are `dot8-native-results.txt`, summary `dot8-summary.json`, generated assembly `dot8_exact.s`.

The native instructions and mixed operand sign support are documented in [Clang's AMDGPU builtin reference](https://clang.llvm.org/docs/AMDGPUBuiltinReference.html). Vulkan's existing packed 4x8 dot instruction does not directly expose this 8x4 operation; transferring the idea needs compiler support or a separate native kernel path.

## Current Q4_K layout follow-up

`check_q4_dot8_layout.py` checks the nibble extraction used by the current megakernel's op28, rather than assuming contiguous synthetic weights. All 256 block indices are covered once; each 16-element partial dot stays inside one 32-element scale group. The lossless activation decomposition passes all 4,096 scalar uint4/int8 combinations and 160,000 random partial dots from 10,000 blocks. Results and the reference shader hash are in `q4-dot8-layout-proof.json`. This is CPU arithmetic/layout evidence only. Float scales, minimum correction, and reduction order remain obligations for any implementation.

There is no factor-of-two reduction in dot instruction count for full int8 activations: 16 values require four dot4 instructions today, or four dot8 instructions after low/high nibble decomposition. The potential benefits are unpacking work and register pressure. Weight bytes do not decrease, and activation packing adds work. This explains why the earlier bandwidth-oriented microbenchmark can remain flat despite fewer registers. It does not establish the cause of any full model result.

The LLVM AMDGPU dialect documents mixed-sign i4 dot support on gfx11 and later: https://mlir.llvm.org/docs/Dialects/AMDGPU/ . The local SPIR-V frontend accepts the packed 4x8 format and rejects other packed formats in vtn_alu.c; a HIP builtin is not directly available to the Vulkan shader. A viable next implementation would need explicit compiler lowering plus exact block-scale handling, or a separately integrated native path. A host Clang upgrade alone does not supply that lowering to ACO. No production repack or runtime change has been made.
