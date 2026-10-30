# Tensor metadata attribution

Extend only CPU observation of synchronous tensor setters: immediately copy tensor name/type/op/flags and requested bytes into bounded4096-key counters. No retained tensor pointers, overflow must be zero. Four fixed native128-request-token profiles after two warmups; all six native129tokens/74drafts/55accepts and no new GPU errors required. Same previously built runner, copy2driver/cap400/native commands/shaders; planning reuse forced off. No optimization/speed inference from instrumented timings.

Compare metadata call totals to1850 per measured generation and prior API count/size histograms. Map actual names/flags to pinned aa8 scheduler/graph source before choosing a change. Names copied on call entry; graph lifetime need only cover its normal API call. No source/destination transfer semantics or ordering changes.
