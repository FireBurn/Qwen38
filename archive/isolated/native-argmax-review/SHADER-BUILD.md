# Shader build used for the tested wide prototype

The shader was compiled before qualification with:

```
glslc -O --target-env=vulkan1.2 argmax-wide.comp -o argmax-wide.spv
spirv-val --target-env vulkan1.2 argmax-wide.spv
```

Both commands succeeded. The exact tested SPIRV SHA256 is in wide-build.json and confirmed-wide-native-path.json. No debug/profiling compile flags. The shader is specialized by the existing native host pipeline's constant0 (originalnative lane count), while physical local size is fixed256. Inputfloat/outputI32 and original24-byte push constants remaincompatible. A privatehost option selects it only for the testedR9700; no system installation or production environment change.

build_wide_host.py reconstructs the privatehost from preserved production-native-shaders/host parent, pinned aa8headers, copied generateddeclarations and existing private readonly shader/buffer/debug objects. wide-build-inputs.json records all header/object/source input hashes; wide-host.patch gives the smallhostchange. It does not rebuild or modify Claude's objects. Originalprivateoff remains the control. Successful build and failedfirstpointer-typeattempt are preserved separately.
