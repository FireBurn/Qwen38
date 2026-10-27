# Two-token recurrent-state operator qualification

Native Vulkan, reference mega and all-matvec two-column prototype pass the same synthetic GDN graph exactly. S=128, H=1, one sequence, scalar gates, two tokens and K=2 snapshots. The graph compares one two-token call with two dependent one-token calls. Both attention outputs, the final state, and the earlier rollback snapshot are bit-identical. A further one-token call starting from the earlier snapshot exactly reproduces the serial second-token output and state. All three modes produce identical raw output files.

40 repeated graphs per mode; final32 graphs entirely mega in both mega modes. Physical mega grid16; the existing native S128/8-columns kernel uses16 workgroups per head. Exact private backend and frozen RADV mappings verified inside the harness. Guard exited0 and resumed the exact original quiet portfolio waiter. Sources, binary, host and SPIR-V pinned in assets.json.

This is a recurrent operator test, not complete controller rollback. It does not cover KV cache, SSM convolution history, multiple heads/sequences, vector gates, graph reuse with changed inputs, model logits, attention masking, accepted-token handling or a different replacement token after rejection. No throughput conclusion or full-model MTP qualification follows.
