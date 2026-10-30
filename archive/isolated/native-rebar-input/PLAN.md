# Native mapped-VRAM input experiment

Measured metadata attributes1850synchronous tensor-set submissions per128requested-token decode to native scheduler input copies (Vulkan0#...#0). Harness historically sets GGML_VK_DISABLE_HOST_VISIBLE_VIDMEM=1. Native aa8 buffer implementation otherwise prefers DEVICE_LOCAL|HOST_VISIBLE|HOST_COHERENT when available and directly memcpy-writes small mapped VRAM destinations. This is an existing per-process backend option, not a system/BIOS/driver change or new ownership path.

Test same immutable qualified Q3/cap400 library/shaders, with only that disable variable absent for the candidate. Keep prefer_host_memory unset, so device-local allocation remains preferred. Native largeBAR writes >=4MiB already use DMA in aa8 source. Retain copy2driver, all queues/fences/order/native activation policy. No shaders, core, clocks, desktop or installed changes.

First short32 freshstock/unmappedfrozen/mappedfrozen fulltargetbit/token/counter qualification; then coding/math128,populatedKV64,boundary128 before timing. Use metadata observer separately to prove actual mapped path via submit count changes; unsupported mapping may fall back natively and must not be claimed active. Monitor new GPU errors and stable library mappings. No adoption/speed claim before fixed matched fullmodel A/B.
