# Mutable descriptor aliases

## Finding

The megakernel binds the same storage through multiple typed descriptor arrays. It must describe those aliases, and cannot promise that the underlying mutable storage is immutable to accesses through its read views.

Local Mesa source (clean HEAD c5b79163126235478466b7b429a370cd7f16f9d3):

- `src/compiler/spirv/vtn_variables.c` initializes SSBO access with ACCESS_RESTRICT for Vulkan memory models and clears it for Aliased.
- `src/compiler/nir/nir_opt_access.c` grants CAN_REORDER to NON_WRITEABLE accesses unless VOLATILE is present.

This explains the observed controls without requiring an AMD cache bug claim. Official specification: https://docs.vulkan.org/spec/latest/chapters/interfaces.html and https://registry.khronos.org/SPIR-V/specs/unified1/SPIRV.html .

## Distinguishing checks

All use the same full 256-thread megakernel with FA, 128 physical workgroups, and the isolated numeric-slot host library.

| Variant | Short output vs existing full control | Long output |
| --- | --- | --- |
| Add Aliased, retain volatile | Bit-identical | Bit-identical |
| Add Aliased, remove volatile, retain readonly/writeonly | Fails, max KL vs stock 13.20 | Not run |
| Remove volatile, retain access promises, no Aliased | Fails, max KL vs stock 13.58 | Not run |
| Remove access promises and volatile, add Aliased | Bit-identical | Bit-identical |
| Remove access promises and volatile, no Aliased | Fails, max KL vs stock 15.03 | Not run |
| Correct source declarations, add Aliased before optimization | Bit-identical | Bit-identical |

Short prompt: 37 tokens. Long: 3,068 tokens. Each original check contains nine full-vocabulary logit frames. These establish regression behavior against the full shader, not a PPL or rollback qualification against production.

## Reproduction

- `build_aliased_views.py`: first three binary diagnostic variants; records transformations in `.decorations.json`.
- `build_mutable_alias.py`: clears access promises on the 27 coherent mutable VIEW buffer types, adds Aliased to descriptor variables, removes 835 volatile memory annotations. Includes the missing-alias diagnostic.
- `build_alias_source.py`: corrects the GLSL access declarations, compiles without optimization, adds descriptor Aliased annotations, then optimizes and validates. This is the source-based candidate for further work.
- `run_alias_stress_checks.py`: separate 65-frame regressions after both prompts against the existing full shader, replaying its generated token sequence.

Pointer visibility/availability operands, memory barriers, state layout, FA layout, and arithmetic remain. Immutable weight views keep their readonly access declarations. Copied `.comp` files beside binary-only postpasses are provenance, not a complete description of the transformed binary; use the corresponding builders and JSON reports.

## Performance

Removing volatile with correct aliases gives 27.233 tokens/s between existing full-control anchors 27.298 and 27.251. Explicit aliases while retaining volatile give 27.219 between anchors 27.161 and 27.242. Neither is an established throughput gain. Register allocation remains 192 VGPRs, LDS 30,720 bytes. This is a correctness improvement and a sound basis for future optimization; it does not beat stock (~31.7 tokens/s).

The 65-frame regression passes bit-identically after both prompts. File hashes for the source candidate, binary, builder, host library and stress results are in `alias-manifest.json`.
