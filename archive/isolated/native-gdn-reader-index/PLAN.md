# Per-graph GDN reader index

Source-backed hypothesis after separate profiling: repeated GDN tail-reader scans take about101msCPU per128-token generation in the instrumented frozen/cap400 host. One graph-local index can replace repeated remaining-graph scans without retaining Vulkan commands or adding GPU memory. No throughput gain inferred from profiling.

Index every source t and t.view_src whose root op is GDN, retaining original node index and source tensor pointer. Query applies the exact original post-node/skip-copy/exclude-source/view-offset predicate. Keep all existing nearby-copy, shape, contiguous-layout, alias and intervening-write checks. Rebuild index every graph; no cross-graph pointers/cache. Core graph metadata must remain immutable during graph compute, as in the pinned source. No shader/command/submission policy changes.

Modes0legacy/1indexed/2indexed+complete legacy decision oracle. Mode2 logs comparisons, uses legacy result on any mismatch, and cannot qualify if mismatches occur. Timed modes use explicit0/1 with matching environment shape and no instrumentation/oracle/logging. Frozen configuration untouched.

Qualification before timing: short32full-vocabulary target logits versus freshstock/reference75055..., release1 andoracle2; coding/math128, populatedKV64 and KV256→512 boundary128 targetbits/counters; oracle comparisons must be nonzero and mismatch-free,including actual fused decisions. Correct mappings/hashes/privatecopy2driver,.27/.7cores,cap400,greedyMTPmax1/q8KV,1CPUthread. Serialguard,noquietgate,CPU/buildloadallowed.

Timing after qualification: fixed24fresh512token arms,six alternatingABBA/BAABblocks,mode1vsmode0 same uninstrumented newlibrary,cap400/frozenQ3shaders. ExternalCPU<=5pp,buildmean spread<=2,runnable spread<=max(4,15%mean),stablemappedlibc inode,validmandatorytelemetry,noGPUerrors,identicaltokens/counters. Naturalclocks/power are outcomes. >=4matchedblocks required;all6andmatched results retained,df3/4/5 descriptive95%t. No outcome-driven extension. If positive,independent comparison against preserved qualifiedfrozen400 still required. No adding historical percentages,mega or arbitrarycontext claim.
