# Next work

Read STATUS.md, CPU-DIAGNOSTIC-PLAN.md and completed analysis before choosing another experiment. Do not retry or extend the failed fresh24 dataset. Keep qualified frozen400.

If resident graph CPU falls but wall time does not, investigate GPU/CPU overlap and dominant weight traffic before investing further in planner micro-optimizations. If validation dominates, inspect repeated full ordered-node/use-count scans across eight stale entries. A future implementation could gather current use counts once, or reject mismatching root metadata sooner, but must preserve ancestor-before-descendant validation and all numerical/mutation witnesses. No implementation or gain is implied by this hypothesis.

A CPU improvement alone is insufficient to adopt: an uninstrumented, predeclared fresh A/B against the frozen configuration must separately establish an incremental model gain under matched external load. Never add historical percentages or pool changed harnesses.

Only megakernel-review is writable. No GPU overlap with Claude, serial guarded GPU launcher, no desktop/system/clock changes or default4DW transfer repro. Native shaders/normal command ownership remain in use. No faster mega kernel has been established.
