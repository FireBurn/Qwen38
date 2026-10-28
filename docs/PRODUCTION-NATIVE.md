# Native quantizer / Q3 checks on the production backend

**The two individual shader changes pass the tested production model target-logit audit. No speedup is established.** This uses the preserved production source/library stack at `aa8ab0504`, GGML 0.27 and llama/common 0.7, with the same private Mesa driver and copy2 path. It is distinct from the older 0.24 experiments and from a current-system deployment.

## Private host and operator controls

The production Vulkan backend is split across translation units. The private port leaves shared structure layouts and original shader/buffer objects unchanged. It adds a per-device module map only in the main translation unit and retains the original lazy pipeline factory. Source/build inputs were read and copied; Claude's source and build outputs were never written. Tracked production source state was clean. [Source state](../archive/isolated/production-native-shaders/source-state.json), [build proof](../archive/isolated/production-native-shaders/host/build.json).

Both shader replacements are disabled by default. The release-style host has no dispatch counting. A separate validation host wraps main-file dispatch calls with atomic counters, allowing actual recorded dispatches to be checked without changing shared headers. It is not a timing build. [Validation build](../archive/isolated/production-native-shaders/validation-host/build.json).

C1/C2 × four quantizer/Q3 settings all match their own production operator control byte for byte. The focused workload covers Q3_K, Q4_K, Q5_K and Q4_0 consumers. Counters verify that the candidate shaders execute and replace their native equivalents. No new target-driver errors were recorded. C1 differs numerically from the old 0.24 control, so cross-version equality is not assumed; each candidate is compared with its own same-stack control. [Results](../archive/isolated/production-native-shaders/operators/checks.json), [comparison](../archive/isolated/production-native-shaders/operators/comparison.json).

## Model target-logit audit

An own correctness-only runner records every requested full-vocabulary target-logit row after its target process calls. It also checks batch metadata, generated tokens and drafting/acceptance counters. Exact backend, model-core and driver library mappings are verified. The core and draft implementation are unchanged.

All four settings—native, quantizer-only, Q3-only and both—match:

- 38 full-vocabulary target-logit rows across 20 target batches;
- 37,745,416 captured bytes, SHA-256 `75055a49a5844ad14030f45cb76c11de20a44a6bb0e2db7c1c89a616137eb576`;
- all 34 generated token IDs, with 19 drafted and 15 accepted;
- 4,738 quantizer and 1,560 Q3 dispatches substituted when enabled.

The stock activation policy is retained. The old private head optimization and SwiGLU fusion are absent. [Per-arm results](../archive/isolated/production-native-shaders/model32/checks.json), [comparison](../archive/isolated/production-native-shaders/model32/comparison.json), [runner build scope](../archive/isolated/production-native-shaders/model-audit-build.json).

A fifth run uses the **unmodified production backend library** with the same audit runner, core and driver. Its complete target-logit capture, tokens and counters match the private default-off control and all candidates. The earlier production 17-token prefix also matches. This anchors parity to the unmodified library rather than only to our modified host. [Stock control](../archive/isolated/production-native-shaders/stock-model32/comparison.json).

## Limits and next work

This captures requested target logits, not target hidden states or internal draft-score bits. It therefore does not have the older instrumented core's complete target/draft audit coverage. It is a 32-requested-token test, not arbitrary long-context qualification.

Audit getters synchronize work, and validation counters add overhead. Neither is suitable for timing. Performance must use the separate release-style host and a timing runner without audit instrumentation. The [production SwiGLU fusion port](PRODUCTION-FUSION.md) now has separate operator and short target-logit checks. Longer production prompts, broader numerical checks and quiet matched full-model timing remain pending. No faster-than-native mega kernel or production model is established. [Detailed notes](../archive/isolated/production-native-shaders/STATUS.md).
