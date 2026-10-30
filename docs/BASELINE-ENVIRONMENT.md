# Benchmark environment and native defaults

The archived “stock” reference uses an unmodified production binary with explicitly selected model arguments, driver and runtime environment. Its environment includes `GGML_VK_DISABLE_HOST_VISIBLE_VIDMEM=1`, `GGML_VK_ALLOW_GRAPHICS_QUEUE=1` and a4GiB suballocation block. Controlled comparisons held those settings equal between arms.

The new transfer investigation identifies an important consequence: disabling host-visible VRAM forces small synchronous input writes through temporary command submission and fence waits. Native aa8 Vulkan code normally prefers device-local, host-visible, coherent VRAM where available, and can write these destinations directly. The inherited shell environment has none of these overrides; they are set by the experiment harness.

The previous gains and losses remain evidence for their archived configurations. Their applicability to normally configured stock requires a separate comparison using native allocation defaults. Restoring one native default is useful correction to the harness, and should be described as such. It establishes no new shader optimization by itself.

The [mapped-VRAM experiment](NATIVE-MAPPED-VRAM.md) holds the previous qualified binary and all other settings fixed, unsetting only the disable flag. A direct unmodified-stock/default-allocation control is required before a broader stock-performance claim. The fixed model policy still includes MTPmax1, greedy decoding, q8KV, FA and4096context on the pinned production.27/.7/private-driver stack; performance is workload-specific. Natural clocks/power remain outcomes.

No installed environment, BIOS, system package, desktop, clock or affinity setting is changed. All new environment choices apply only to private benchmark child processes.

## Direct default comparison

The [three-mode native-default controls](NATIVE-DEFAULT-BASELINE.md) now pass530fulltargetrows each, with all four legacy overrides absent. Their fixed72-run comparison is in progress. Separately, mapped-VRAM restoration is independently confirmed at+28.3% over the previous constrained harness; this result is not pooled with the new direct-default comparison.
