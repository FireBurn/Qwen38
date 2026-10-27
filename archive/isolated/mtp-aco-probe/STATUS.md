# Current MTP shader on private ACO compiler

Frozen private driver SHAabb4efb084228b87fbd944db441b16b70f74358bcc14489708d226e2d1fff5fd, same driver previously qualified on older single-token shader. Private compiler baseline differs from installed nearest-containing-WMMA LICM filter; extra cross-descriptor scheduling remains separately off/on. Installed files and Claude sources unchanged.

First16-workgroup Q5_K K5120/R4097/two-column operator probe:4same-pointer input patterns,0/1/2bias outputs,64graphs, final16fullymega. Off/on/wrong-fingerprint all byte-identical to native. Wrong fingerprint reproduces off code hash.

Current MTP shader fingerprint:7998blocks,15696logicalLDSbytes,96VGPR,fingerprint7494240752530963822. Hardware LDS allocation16384. Private off/on both9scalarspills,0VGPRspills,0scratch, compared with38scalarspills in frozen installed compiler. The spill reduction comes from private baseline compiler changes, not from enabling cross-descriptor scheduling. Code off425004,on424812bytes; installed425964. Resource envelope supports previously qualified192-workgroup grid.

192-workgroup actual MTP correctness audit complete for Roman and C++ prompts, requested64tokens: each driver mode matches installed reference213binary logit/hiddenrecords exactly (114Roman+99C++), all emitted66/65tokens and acceptance28/38,32/33 identical. Last12graphs have zero native fallback. Narrow finite prompts/greedy decoding do not establish stochastic or long-context quality.

One model harness assertion failed because acceptance counters overwrote fingerprint variables before on mode; child exited normally with policy disabled. Failure archived under model/harness-enable-attempt, variable separated and corrected enabled run qualified. No GPU crash.

## Performance diagnostics completed; no adoption

Six-arm streamed microbenchmark installed/off/on/on/off/installed,512iterations each,8alternatingQ5_K/Q4_K matrices,K5120/R17408/two columns,445644800logical weightbytes/graph. All outputs byte-identical. Means installed0.8215ms/privateoff0.8205ms/privateon0.8200ms. Apparent0.183%reduction is below installed control drift0.366%; no established benefit.

Original asynchronous MTP pipeline8-arm native24/installedmega/privateoff/privateon/privateon/privateoff/installedmega/native24,requested128/emitted129tokens. Means native44.767t/s,installedmega39.000,privateoff39.0675,privateon39.1885. On vsinstalled+0.483%, off+0.173%, while installedmega drift1.597%,native1.232%. Privateon remains12.461%slower than native. Every129token stream and acceptance55/74 matches; no repeated optional timing.

Three external compiler processes remained active; generationCPU22.7-23.5%, clocks3101.5-3151MHz. This is diagnostic under load, not quiet adoption evidence. No precise subpercent gain claim. Original async pipeline used, not synchronized stage-profiling runner. Same .24core/Q8policy in all arms; no production.27 ABI comparison in this batch.

Decision: no adoption or current-model promotion. Retain exactness-qualified driver as research control; reducing38to9scalarspills has not established useful model performance. It does not prove all scalar spills irrelevant, but rejects spill-count reduction alone as evidence of a solution. Next priority is phase-level attribution of operator execution, work distribution and grid-barrier time inside target verification. Prior older-shader quiet ACO queue remains unchanged.

Both guards completed and resumed original quiet portfolio waiter. No GPU failure or system-driver/Claude source changes.
