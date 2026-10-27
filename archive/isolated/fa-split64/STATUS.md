# 64-position FA partitions

Private host experiment, reference shader and192 workgroups unchanged. Narrow opt-in GGML_VK_FA_SPLIT_KV64=1, exact R9700/Q8/GQA6/single-token/head256/<=4096KV guard. Changes the split before scratch reservation and both FA/reduction PC construction. CPU audit proves partition coverage and scratch ownership for every padded KV64..4096.

Measured short mega output is bit-identical to saved mega reference. Nine long frames preserve all argmax, meanKL6.5585e-5/maxKL2.4055e-4, maxabs0.15234. Native cross-check diagnostics are separate: the saved native-subgroups oracle is the MEGA reference, so native64-vs-that oracle conflates native/mega arithmetic and must not be labeled an isolated split comparison. The original combined runner stopped on that conflated long-native gate; run_fa_split64_mega_checks.py correctly compares mega64 versus original mega. No numerical gate was relaxed to qualify the mega change.

Quiet ABBA: control29.744004 vs candidate29.796084t/s (+0.1751%). Control drift0.4765%, max individual RSD0.4661%. Gain is below observed variation; no demonstrated improvement, no fuller benchmark or promotion. No fixed-text qualification of changed accumulation order claimed. See microbench-fa-split64-96.
