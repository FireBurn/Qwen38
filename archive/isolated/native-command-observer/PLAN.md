# Native command observer

Observer only: never skip, reuse or alter GPU commands. Clone the qualified guard-v2 host into this directory, rebuild all three host translation units and add a separate observer object. No shader or backend-context layout change. Qualified configurations remain untouched.

Capture exact native dispatch pipeline/layout/set handles, workgroup dimensions, descriptor buffer/offset/range tuples and full push-constant bytes. Capture synchronization, fills/copies and command-sequence boundaries where instrumented. Store submission handles/timeline values separately from program content. Mark unsupported commands explicitly; do not claim complete replay identity when coverage is incomplete. Outside-graph uploads/transfers and pool ownership remain outside any replay proof.

Compare complete captured byte vectors within context/node-count/buffer-generation/entry-state groups. FNV64 is a display index only; equality must compare full bytes. Record raw metadata locally, bounded to128MiB/1024unique programs. No tensor data is captured. Observer timing/I/O cannot establish speed gains.

First qualification uses32requested-token target-logit audit versus native75055... . Then coding/math128 and populatedKV64 target bits, and inspect repetition/changed fields. Native shader geometry and all original GPU commands remain unchanged. Copy2/private driver, .27/.7cores, greedyMTPmax1/q8KV, cap400 and serial guarded GPU execution. CPU/build load allowed; no system settings or Claude changes. No replay implementation or performance claim.
