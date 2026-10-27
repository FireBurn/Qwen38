# Matrix family allocation audit

Build session81041 and guarded device session6584 both terminal0. Private reachability partitions retain original arithmetic and original memory/barrier protocol. All first-device launches16groups. Actual mapped frozen RADV checked; outputs match saved native Q4/Q5 C1/C2 reference byte for byte.

| Retained family | VGPRs | LDS bytes | Pre-schedule VGPRs | Code bytes |
| --- | ---: | ---: | ---: | ---: |
| Q4_K/Q5_K C1/C2 |60|0|42|84212|
| Q6_K C1/C2 |72|2048|57|22012|
| BF16 C1/C2 |48|0|25|34064|
| Q8_0 C1/C2 |48|0|39|31288|
| Q4_0 C1/C2 |48|0|21|15460|

All zero scratch and zero reported SGPR/VGPR spills. Earlier Q3 pair uses48VGPR. Combined matrix group uses96VGPR,2048LDS, pre-schedule66. Thus none of the isolated matrix families requires96. The combined allocation is not simply the maximum of independently compiled paths. Whole-program live ranges, control flow, or schedule/allocator choices are the next suspects; this experiment does not distinguish those mechanisms.

Coverage limitation: the client exercises retained arithmetic only for Q4/Q5. Other modules are compiled into real pipelines and their allocations observed, but the Q4/Q5 client falls back native. Do not treat matching outputs as correctness coverage of Q6/BF16/Q8/Q4_0 retained arithmetic. These are diagnostics, not integrated model candidates or speed measurements. No fuller performance run is warranted for partial partitions.

Next: construct cumulative or leave-one-family-out matrix partitions to locate the interaction that raises pre-schedule66 and allocation96. Inspect relevant live ranges/ACO assembly before modifying arithmetic. FA independently still requires96/16KiB, so a complete unified improvement needs both resource limits addressed. Preserve full FA and all model operator eligibility in any adoption candidate.
