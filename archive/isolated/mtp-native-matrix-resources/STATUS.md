# Native matrix allocation audit

Three native clients at5120x17408, one timed iteration after warmups. This is a resource audit, not a performance comparison. Full actual dispatch keys and all native pipeline stats retained. Repeated audit91259 verified frozen RADV via /proc maps and compared every output SHA against the first run.

Observed native Q3K,C1/C2:48VGPR,0LDS,0scratch. Q4K/Q5K,C1/C2:48VGPR,0LDS,0scratch. Q6K,C1:48VGPR,1024LDS,0scratch. Some spec instances share display names; preserve dispatch keys and resource sequence rather than asserting an undocumented name-to-spec mapping.

Unified mega allocates96VGPR/16KiBLDS. This is a concrete allocation difference, not proof of actual active-wave counts or causal speedup. Hardware workgroup limits, geometry and scheduling also affect residency. Partial reachability diagnostics in ../mtp-resource-partitions will isolate which opcode combinations raise the demand. No hybrid configuration is an adopted solution to the unified-kernel objective.
