# CPU fusion-plan reuse with native memory defaults

Distinct interaction experiment: reuse existing immutable be19a3c9 library without rebuilding it. Earlier CPU graph-time reductions were measured with forced nonmapped VRAM and did not establish token gains. This experiment removes all four legacy allocation/queue/suballocation overrides. Keep Q3 padding/cap400, original core, MTP1 and pinned copy2 driver unchanged. This does not establish superiority over stock100 by itself.

First qualify all five cases (530 target rows) against native target bits/tokens/counters. Modes2 oracle and1 reuse must show actual hits, zero mismatches, no driver errors; fresh short case also includes stock400 and frozen400 controls. Native-default three-arm results provide the independent reference for the environment. Retain strict device options, lifetime/buffer epochs and GDN pointer guards. No command buffer replay or new shader.

Do not run during default72 timing or any conditional confirmation. No own compile is needed. Qualification only, no timing interpretation from audit processes. A separate fixed-sample matched-load timing plan is required before any subsequent performance measurement. No pooling old/new runs or adding CPU percentages to token speed.
