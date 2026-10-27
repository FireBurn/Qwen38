# Bounded packed activation cache

Separate shader candidate; no production or Claude changes. Cache-on/off use identical SPIR-V with different operator mappings. Only Q5_K/Q4_K two-column K5120/6144, R>=4096, single-batch contiguous layouts qualify. Packed inputs overlay existing 16KiB LDS and retain coherent global reads before a workgroup barrier. Other cases keep the original path.

Build and spirv-val passed. Initial 20 cases: native/parent/cache-off/cache-on across two eligible large shapes (including odd R4097), small-R, large-K and single-column fallbacks. Each case changes inputs in place through ordinary/zero/scaled/tiny phases and tests zero/one/two bias additions. All outputs byte-identical to native, 64 graphs per case; candidate final16 graphs have no native fallback. Push constants in eligibility-proof.json confirm eligible shapes actually qualify.

Resource dump: 96 VGPR, 38 spilled SGPR, 0 spilled VGPR, 16384 bytes LDS, 0 scratch. Same allocation as parent; code size grows from425964 to485756 bytes. Compiler-generated SPIR-V marks all9 shared variables Aliased; shared-alias-proof.txt verifies overlay declarations. First tests used 16 physical workgroups.

## Diagnostic completed; candidate shelved

192-workgroup streamed GPU timestamp diagnostic: 8 alternating Q5_K/Q4_K matrices, K5120/R17408, two columns;445644800 logical weight bytes/graph,512 iterations per run,6 parent/off/on/on/off/parent runs. Every run is finite and byte-identical across batch/separate columns and all modes.

Means: parent0.840ms; same-module cache-off0.842ms; cache-on0.883ms. On is5.12% slower than parent and4.87% slower than same-module off. Aggregate control drift4.6%, candidate6.1%, with external compilers and changing clocks: these are under-load diagnostics, not precise quiet performance results. Final reverse pass on/off/parent is0.909/0.861/0.859ms at median1688.5/1678/1677.5MHz; also no cache advantage at closely matched clocks.

Decision: shelve; no adoption, no claimed model speedup. Whole-model audit script prepared but not run because the microbenchmark provides no reason to adopt this candidate. The byte-exact isolated results do not establish whole-model correctness. Existing parent model remains unchanged.

Evidence narrows the search: simply staging packed activations in LDS does not recover the target-verification gap on these shapes. It does not prove activation loads are free or identify a unique bottleneck. Shared-copy/barrier costs versus existing cache reuse need counters to distinguish. Next higher-priority direction is compiler/register pressure: current mega has38 scalar spills; a prior separate private Mesa baseline reduced older-shader spills, but this larger MTP shader requires fresh resource/correctness and same-driver off/on qualification.

Guard completed successfully and resumed original quiet portfolio waiter.
