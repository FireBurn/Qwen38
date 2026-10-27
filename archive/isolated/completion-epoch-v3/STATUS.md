# Completion epoch and active counter reset, ABI 3

Private candidate; current reference is unchanged. No throughput gain established.

The shader separates arrival and completion into distinct 256-byte cache lines. The last arrival publishes the completed epoch; other groups poll that epoch with device-scope acquire loads. Workgroup/device buffer handoffs remain acquire/release. The header is 512 bytes. Operator arithmetic, FA, and the 192-group grid are unchanged. Actual resources remain 96 VGPR, 24 spilled SGPR, zero spilled VGPR/scratch, 16 KB LDS, 241132-byte code. Capacity 256; retain 64 groups spare.

The host clears only the active header and per-record counters immediately before each dispatch. Oversized or unowned segments use a dedicated tail after the 4 MiB segment pool, avoiding overlap with future owned segments. All prior GPU barrier calls remain. Accept only 256/512-byte header metadata. Allocation is 4,456,960 bytes.

CPU evidence: protocol randomized scheduling (256 schedules, 64 phases, up to 256 participants); SPIR-V scope/layout audit; reset-plan witness extracts actual backend blocks and checks 180 boundary cases. Simulated writes expose the previous ABI1 prototype overlap at 4000 records and the original reference overlap at 4100 records, then verify ABI3 keeps the next segment clean. This is a generic capacity-boundary witness, not evidence that measured target graphs or reported desktop crashes exercised the case.

GPU evidence: initial resource probes at 1 and 16 groups; odd-row operator parity; 16 distinct changing-input witnesses; all three 9-frame model checks exact; both short/long 65-frame checks bit-identical. Last 32 graphs have zero native operations including FA, with 2772 gather elisions per sequence. Host-only ABI3 with original bounds shader separately passes both 65-frame checks. In-child /proc/self/maps verifies the loaded backend. Both use the frozen private RADV/SPIRV-Tools snapshot; other system dependencies are not frozen.

Performance: queued in run_verified_portfolio.py with current reference and integer one/four-row candidates. Requires 30 seconds compiler-free and <=20% aggregate CPU busy, runs serially, stops only its own benchmark process group on competing work, preserves interrupted batches. No speed claim until completed stable results. Never substitute older completion-epoch or completion-epoch-v2 hosts.
