# Compact FA query storage

Private experiment only. Current reference unchanged.

The captured FA has six query rows but 16-row hardware matrix operations. This variant keeps 16x16 WMMA and stores eight logical query rows. Manual fragment loads zero inactive columns. Direct scalar Q8 V loads remove the 8 KB V staging requirement that previously prevented Q storage compaction. All existing barriers remain.

CPU audit: host shape guard positive and negative tests; unique score, probability and output writers; fragment load bounds; simultaneously live shared-memory intervals do not overlap. See audit.json and audit.py. Hardware fragment mapping is pinned to gfx1201 wave64 and the private/installed Mesa revision; no portability claim.

Installed driver: short and long nine-frame checks both bit-identical. Actual allocation 96 VGPR, 22 spilled SGPR, zero VGPR spills/scratch, 8192 bytes LDS. Original-source private ThinLTO Mesa also passes both nine-frame checks: 96 VGPR, seven spilled SGPR, 8192 bytes LDS.

Occupancy arithmetic: 768 wave64 VGPRs per SIMD, two SIMDs per CU and four waves per workgroup. At 96 VGPR, capacity is 256 workgroups over 64 CUs; safe tested target is 192. If scheduling reaches 72 VGPR, capacity is 320 and the target with 64 spare groups is 256. In particular, 72 VGPR does NOT justify launching 320 groups. The 12 KB variant already has the same 320-group capacity at 72 VGPR; 8 KB alone does not guarantee a further occupancy gain.

ACO default trace for this exact shader: blocks=6027, lds=7888, usage_vgpr=63, usage_sgpr=108, waves=10, min=2. A margin-six experiment is guarded by all three exact resource fingerprints and uses its own shader cache. No larger launch before measured resources and correctness gates.

No throughput result yet.

Both installed192 and guardedmargin6/256 pass65-frame short and long checks exactly. Every last32graph has zero native operations, including FA. First six-run throughput comparison is inconclusive: control27.9503→26.4016t/s (5.54% drift); individual repeat standard deviations reach10.38%. Background Rust build was active during early runs and exited during the sequence. Apparent compact+3.336% and margin6+0.462% means are NOT speed claims. Raw data microbench-fa-compact8. A separate settled retry starts only without CPU compilers, aborts our own child if one appears, and records read-only GPU clocks/busy telemetry in microbench-fa-compact8-settled.

Quiet retry COMPLETE: control29.8333825t/s, compact19229.7552115 (-0.2620%), margin6/25629.7032535 (-0.4362%). Control drift0.3778%, no CPU compilers detected, all individual repeat standard deviations below0.4%. This is sufficient to reject a demonstrated speed gain; no optional fuller benchmark and no promotion. Smaller LDS and lower VGPR are verified resource changes only. See microbench-fa-compact8-settled.
