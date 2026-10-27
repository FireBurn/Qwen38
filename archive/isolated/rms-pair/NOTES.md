# Independent RMS pair candidate

CPU audit finds 48 adjacent RMS pairs in the saved full graph. Each has identical 29-word parameters, grid16/1/1,2048 elements in128-element rows, disjoint outputs and no cross-output reads. After existing norm-scale fusion their post-scale/bias fields must also match; runtime guards must check this explicitly.

A possible compound record doubles the virtual grid to32, routes each physical workgroup to one source/output pair, subtracts the half-grid offset before the unchanged RMS routine, and keeps each workgroup's local barriers. Do not use per-subgroup routing: RMS uses workgroup shared reductions. Skip the second record and compact duplicate grid barriers.

Run this pass after BF16-pair fusion so it does not destroy that pass's expected two-RMS pattern. Preserve both norm outputs and all norm-scale arithmetic. It needs a capability header and an opt-in host flag, source/overlap guards and both check depths before timing. Not implemented or measured yet.
