# Matched mixed-matrix streaming diagnostic

Settled3 guarded batch77365 terminal0. All48cases native bit-exact (all intermediate outputs), batch/serial exact, zero background builds in measurement and all clock/CPU gates pass. Six-case16WG qualification also passed. Frozen same private driver/backend for native/original/keep. Original96VGPR192WG versus combined72VGPR256WG includes several kernel changes; it does not isolate register policy alone.

| Shape | Graph | Columns | Native us | Original us | Keep us | Keep extra time |
|---|---|---|---:|---:|---:|---:|
| 5120x17408 | independent | batch | 802.91 | 994.93 | 987.44 | 22.98% |
| 5120x17408 | independent | single | 1526.05 | 1741.98 | 1741.29 | 14.10% |
| 5120x17408 | chain | batch | 807.34 | 998.53 | 996.05 | 23.37% |
| 5120x17408 | chain | single | 1536.94 | 1746.62 | 1756.55 | 14.29% |
| 17408x5120 | independent | batch | 811.91 | 980.91 | 974.77 | 20.06% |
| 17408x5120 | independent | single | 1522.03 | 1730.25 | 1729.93 | 13.66% |
| 17408x5120 | chain | batch | 813.20 | 983.51 | 980.37 | 20.56% |
| 17408x5120 | chain | single | 1531.91 | 1754.78 | 1755.13 | 14.57% |

The unified kernel remains slower in every group. Independent versus dependent graphs have similar gaps. This narrows the next experiments toward matrix execution/scheduling and shared resource footprint; it does not prove atomic contention or a precise memory bandwidth bottleneck. Nominal weight GB/s is bytes divided by synchronized wall time, not hardware-measured VRAM transactions. Host sync calls are not measured GPU barrier latency.

Each pass has8alternating Q3/Q4/Q5/Q6 matrices,445644800weight bytes; batch computes2columns together, single computes both serially and reads nominal weights twice. Compilation and separate>=3second warmup excluded. Current Q6 uses native F32 matvec while Q3/4/5 use MMVQ; aggregate bandwidth interpretation must respect that mixture.

V1 andV2 partial runs are preserved and invalid for performance due to GPU clock ramps. V3 separates compilation from timed-graph warmup and all actual timing gates pass.

Next: adaptive quantized task reservations in ../mtp-adaptive-quant-claims. Initial queue36472 terminal1 from build-wrapper missing imports before GPU launch, corrected manual build/qualification session45230 running. Separate FA global-tile sources in ../mtp-fa-global-tiles, build session16662 running. No faster-than-native or full-model gain established.
