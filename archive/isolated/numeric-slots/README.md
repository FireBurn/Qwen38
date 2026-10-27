# Numeric descriptor keys

Private host experiment. `../prepare_numeric_slots.py` derives a separate host translation unit from the isolated source and rewrites only the descriptor-slot map keys: three uint64 fields (buffer handle, offset, range) replace formatted strings. Full key equality handles hash collisions. Slot zero remains reserved for scratch. Pipeline opcode keys remain strings.

Run `python ../prepare_numeric_slots.py`, then `python build.py` from this directory. This builds a separate Vulkan backend library in `bin/`, leaving the default isolated and production libraries alone. Model runner: `../run_numeric_slots_checks.py`; paired timing: `../run_numeric_slots_bench.py`.

`benchmark.py` extracts the last graph's descriptor accesses from the frozen `../mk/tape_tg.txt`, constructs both maps, then runs ten alternating-order trials of 200 graph lookup passes. It checks matching aggregate slot IDs. This measures lookup work, not total graph recording or model speed. The first measurement covers 7,132 binding accesses and 1,063 unique keys: median 1,872.29 us/graph for formatted strings and 36.05 us/graph for numeric keys. Background compilation was active; see the raw trial results in `lookup-results.json`.
