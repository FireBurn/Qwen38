# GLU quantization plus FA K-slice prefetch

Combines two independently correctness-qualified changes with positive focused GPU measurements. Source composition only changes separate QK staging and GLU/quantization code paths; shared compiled-module resources and scheduling may interact. Individual measurements do not qualify the combination.

Build/validation live in build_shader.py; manifest records hashes after success. Qualification completed: four nine-frame checks at 16 workgroups (fusion off/on, short/long prompts), then both 65-frame checks at 192 workgroups. All outputs are bit identical. Each enabled stress run fused 3,402 pairs; the final 32 graphs used no native operations or native FA. See checks.json, stress.json and verified-manifest.json.

Actual allocation: 96 VGPRs, 24 spilled SGPRs, no spilled VGPRs, 16 KiB LDS, no scratch. Capacity is 256 workgroups; testing retained 64 spare. These are correctness and allocation results, not a measured throughput gain.

The quiet baseline / GLU / K-prefetch / combined comparison is queued by run_glu_k_after_aco.py behind the existing serial ACO comparison. It uses eight symmetric runs, 256 generated tokens and four repetitions at 4K context. The runner pins qualified artifacts and waits for 30 seconds without compiler workers, low CPU load and no competing inference. Compiler or inference activity during measurement aborts the comparison. Generic CPU load and clocks are logged throughout; CPU quietness is a start gate, not a continuous guarantee. Current reference unchanged.

Other negative/inconclusive candidates should not be piled into this bundle blindly. Completion-epoch host ABI and compiler fingerprint constraints require explicit separate integration, not environment-variable stacking.
