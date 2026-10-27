# Production-native MTP smoke completed

Frozen production sourceHEADaa8ab0504deda8ef55958aa2c7ccdee3eab924ca/GGML0.27/llama/common0.7 libraries. Private copied runner, matching header/library hashes;backend and frozen RADV map markers verified. All four small native Q4_0execution probes succeeded. Native release has no tape hook; matrix-grid bounds are source-derived, not observed dispatch counters (MMVQ<=3rows, MMQ minimum32tiles and splitK cap8 gives<=16 forR3/N37; alignedK256/R16/N16 uses splitK1). No shader/driver modifications.

Actual production-native greedy MTP shortprobe completes: emits same17tokens as old0.24native/mega MTP and old0.24non-spec controls, drafts10/accepts7. Stock0.27defaultactivation policy retained (privateQ8F32override absent); this is a full-stack comparison, not isolatedshaderattribution. No GPUcrash/nonfinite/externalchange. Guard completed/restored original quiet waiter.

Production-native non-spec17token reference completed and matches full17token production-MTPstream exactly. Need longerproduction MTP/quality controls and quiet full timing. Do not infer speed from logged wallstats while19compilerworkers keep CPUbusy. Historical.27benchmark snapshots remain unchanged;preparedrunneronly addsmapchecks/tokenlogging. Prodtree/installedstack untouched.
