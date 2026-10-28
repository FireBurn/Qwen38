# Experimental shader source

`swiglu-q8-shuffle8.comp` is a standalone experimental SwiGLU plus Q8_1-x4 quantization shader derived from llama.cpp's MIT-licensed Vulkan shaders. See `LICENSE-MIT`. It is not a drop-in backend installation.

Compile using the same arithmetic optimization settings as the tested native backend:

```sh
glslc -fshader-stage=compute --target-env=vulkan1.2 -O swiglu-q8-shuffle8.comp -o shader.spv
spirv-val --target-env vulkan1.2 shader.spv
```

Tested contract: 64-thread workgroup; required full subgroups of32or64; F32 gate/up/output buffers at bindings0/1/2; Q8_1-x4 packed output at binding3. Push constants are `ne` and `num_blocks=ne/256`. Only `ne=17408` and `34816` are qualified here. All eight lanes in each reduction cluster must be active. The native host retains dense-shape/type/alias checks and the existing quantization cache and barriers.

Each reduction uses XOR masks1,2,4 to cover exactly eight lanes. The packed integer-valued sums remain exactly representable. Do not generalize this replacement to arbitrary divergent subgroup reductions. Native/fused output checks, signed-zero and rounding-boundary cases, and captured model audits are linked from [the report](../docs/SHUFFLE8.md).

SPIR-V built from this published source matches the tested optimized SPIR-V byte-for-byte. No binary is distributed. This result does not establish a speedup or correctness for arbitrary shapes, models, or contexts.
