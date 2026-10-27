# LDS/ISA research check

AMD's September2026MI450 article discusses transposed LDS loads and layout/partition conflicts. Its measured gains concern gfx1250 WMMA/Triton, not this gfx1201Vulkanwave64 kernel. Useful layout methodology, no transferable speed claim.
https://rocm.blogs.amd.com/software-tools-optimization/mi450-lds-optimization/README.html

Primary MLIR documentation explicitly limits transpose_load lowering to gfx950 andgfx1250. This is not evidence of an available gfx1201 LDS-transpose intrinsic. Do not suggest simply enabling it onR9700.
https://mlir.llvm.org/docs/Dialects/AMDGPU/

Our frozenACO table supports global_load_tr_b128/b64 onGFX12 and visit_load_global_tr emits them forglobalmemory. That is a different operation from localLDS transpose. CurrentFA K/V data areQ8 and mustbe dequantized intoF16, Q isF32 scaled/converted beforeWMMA, so global-transpose loading is not a drop-in replacement for currentLDS operand loads. A future format/layout experiment needs itsown numerical and traffic evidence.
