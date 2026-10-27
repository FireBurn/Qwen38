# Replay validation experiment

Measured baseline: first-submit-analysis.json. At16 the observed submission-path delay is1.03317ms; wall regression1.38725ms. This is correlation, not an isolated causal measurement. Preserve shader and submission boundaries while changing only validation.

The current key allocates/serializes196952 words and sorts tensor pointers on each requested graph. Proposed replacement retains the full structured key for capture and confirmation, but validates stable hits without allocation/sort:

1. Match owner/device and preallocation sizes, objects, BDA addresses and last_total_flops.
2. Match ordered graph node pointers before dereferencing retained metadata.
3. Match all current node object representations before touching retained source-only tensors. This conservatively validates source edges; incidental header changes may cause safe misses.
4. Match source-only tensor headers and each unique buffer/context/device-buffer/BDA identity. Tensor-header equality alone is insufficient for buffer internals.
5. Match the full2048-slot table. Preserve two identical compiled captures before eligibility.
6. On misses use the original full-key path and rebuild snapshots at the pre-body point, not after backend state mutation.
7. Clear owner cache at backend teardown. Do not infer allocation lifetime from shared_ptr alone: buffer-free explicitly destroys the allocation.

Use existing16 physical workgroups first. Require genuine native195-record equality across KV256→512, cache misses/rebuilds/hits, then192. Profile the same ABBA quartets, including first submission-path entry, before asynchronous throughput. No win based on CPU time alone.

Further isolation if needed: measure time spent in gather-consumer proof and key creation independently. A successful fast key may expose gather proof as another upfront cost. Moving gather proof after a validated hit requires checking that no preamble path consumes its output.
