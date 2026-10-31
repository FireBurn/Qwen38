# Native-default constant rotation cache

Short guarded session 49655 completed successfully: stock, cache-disabled private core and cache-enabled private core each matched 38 raw target rows, tokens and counters. Enabled arm created two caches and bypassed 122 input copies. No new GPU errors. Native allocation, queue, suballocation and submit-cap defaults, no Q3 padding. Longer prompts, populated KV, boundary and repeated-clear checks remain before timing. No speed claim.

Broader guarded session 19029 terminal 0: coding 136 and maths 138 raw rows per private arm, populated KV 72 and boundary 146 raw rows per stock/private arm; all match tokens, counters and raw target bits. Enabled cache created two caches and positive bypass counts, with no new GPU errors. Combined with short 38 rows these cover 530 rows per private mode. Repeated-clear under native defaults remains required; no timing or speed claim.

Repeated-clear first attempt exited before generation: profiling runner requires GGML_VK_Q3_PAD112_DIR even though source never uses pad_dir; no GPU errors. Retry supplies only the required path, without arena activation. No timing data collected.

Repeated-clear corrected run session 2368 terminal 0: six generations match expected tokens and counters after clears, child exit 0 and no new GPU errors. Metadata backend is instrumented; not a speed result. Directory path variable required by runner but Q3 padding arena not enabled. Next: predeclare matched native-default performance comparison.
