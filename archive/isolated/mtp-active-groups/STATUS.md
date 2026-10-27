# Dynamic active-workgroup candidates

Separate parent-derived shaders;17 dynamic allocator wrappers changed. Whole-WG early return occurs before metadata loads and counter claims. Main loop/global barriers preserved, arithmetic unchanged. Spread keeps min(nphys,total logical jobs) WGs; packed keeps min(nphys,ceil(total/SLOTS)). Packed can reduce CU spread; counter counts alone do not predict speed.

First16WG tests:10cases,2variants across5shapes,4changing same-pointer input patterns,0/1/2bias outputs. All byte-identical to native,64graphs/case,final16fullymega. Both96VGPR/38SGPRspills/16KiBLDS/0scratch, same allocation as parent.

Source estimate for sampled target3440-record graph:785dynamic operators, terminal claims602880parent/425472spread/356800packed. Excludes fused normquant bypass and global barrier atomics. These are source estimates, not measured traffic or latency savings.

192WG microbenchmark8smallQ4/Q5 matrices,K5120/R3/two cols,6symmetric runs,8192timedgraphs each: means parent0.132475ms/spread0.128847/packed0.133327. Spread apparent2.74%gain is below6.29%own drift; clocks differed1770-1894MHz. Packed0.64%slower with3.69%drift. Cumulative timestamps exclude first32warmup graphs;1us printed-average resolution. Every run byte-identical acrossmodes and batched/separate columns. No stable micro win.

Full MTP192WG correctness: Roman and C++ requested64 produce66/65tokens,28/38 and32/33acceptance, eachvariant's213full logit/hidden binaryrecords bit-identical to parent. Last12graphs no native fallback.

Original async MTP128requested/129emitted,8symmetric arms: native44.7235t/s,parent39.0200,spread39.0745,packed38.8105. Spread+0.1397%,packed-0.5369%vsparent, parentdrift1.305%,spreaddrift1.373%,nativedrift1.308%. All129tokens and55/74acceptance identical. Threeexternalcompilers,CPU22.6-23.4%,generationclocks3093-3155.5MHz. Under-load diagnostic, no adoption evidence. No useful model gain demonstrated; candidates shelved.

Initial harness failed beforelaunch because executable path pointed to newdirectory instead ofexistingprobe; corrected. No GPU work in that failed invocation. All later GPUchildren exit0 and guards resume exact quietwaiter. No installed/Claude changes.

Next lead: separate the whole-kernel resource ceiling from direct FA execution cost. FA is a tiny portion of short-context measured execution but its LDS and register allocations apply to every operator in a shared shader. A native-FA diagnostic control may test the ceiling hypothesis; final desired design still keeps FA in mega, requiring compact FA storage if the hypothesis proves useful. Must audit other live shared arrays and their lifetime before compacting offsets.
