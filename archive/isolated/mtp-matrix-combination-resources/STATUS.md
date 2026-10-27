# Matrix combination allocation audit

Build75975 and guarded device audit79983 terminal0. All first-device launches16physical workgroups. Same native-RMS parent903442bfd293f999049a93286ff1e182232aefb29f1a6844e41574739647379a, unchanged retained arithmetic and barriers; only unreachable opcode cases and metadata removed. Driver mappings checked. Q4/Q5 output reference matches byte for byte. No model or performance improvement claimed for partial diagnostics.

| Reachable combination | VGPRs | LDS bytes | Pre-schedule VGPRs | Code bytes |
| --- | ---: | ---: | ---: | ---: |
| All matrices except Q6 |60|0|48|225468|
| Q6 + Q4/Q5 |96|2048|61|105332|
| Q6 + Q3 |96|2048|59|82024|
| All matrices except BF16 |96|2048|66|211660|

All zero scratch. Prior isolated Q6=72VGPR/pre57; Q3=48/pre39; Q45=60/pre42. Q6-containing combinations inflate to96 even with just one additional family. BF16 is not required for the increase. All other matrix families together remain60. This localizes a combined-path effect involving Q6, but does not prove whether preRA scheduling, live ranges, or register assignment is the cause.

Coverage: Q4/Q5 retained math executes in no_q6,q6_q45,no_bf16. q6_q3 runs the same client via native fallback; no arithmetic correctness claim for its retained math. Other retained paths also have not individually been exercised in this batch. Resource observations are real pipeline allocations. Partial/native mixes cannot establish an integrated speedup.

Source evidence: frozen aco_scheduler.cpp schedule_program computes usage from all blocks, increases vgpr_demand by12*reg_file_multiple, selects target_waves, and budgets scheduling against registers implied by that target. It deliberately trades occupancy for scheduling. max_suitable_waves also applies LDS and whole-workgroup limits. This explains why isolated and combined demand can choose different budgets; it is not an attribution of every extra register. Earlier blanket/pre-only nosched controls regressed model performance, so do not repeat them as a proposed solution.

Next actionable source experiment: reduce Q6 simultaneous decoded-vector/activation-vector live ranges while preserving each dot-product FMA order and final nested scale/FMA order. Q6 op34 currently keeps four decoded vec4s and four activation vec4s across inner accumulation. Stage the independent dot chains serially, retain original barrier placement and float arithmetic. Test Q6 C1/C2 directly first16 with native references, inspect allocations in both Q6+Q45 and unified modules. FA independently96VGPR/16KiB still needs a separate reduction, e.g. stream per-row eM scaling to shorten its four-element decay array lifetime. Neither change is implemented yet. Do not raise physical grid without a complete resource/capacity gate.
