# Next alternative to typed descriptors

This is an unimplemented experiment plan, not a measured improvement.

The current shared-binding candidate eliminates duplicate descriptor arrays while preserving all typed views and fusions. A further alternative is a table of raw buffer addresses indexed by the same slot IDs. This could reduce scalar buffer-pointer setup, but global-memory address arithmetic and weaker alignment may offset it.

The historical fullbda/gen_mega_bda prototype is not a suitable replacement: it excludes FA, uses old row mappings, assumes 16-byte pointer alignment, and the host fusers require bindless slot IDs. Do not repeat it as a fair full-FA comparison.

## Preserve the current ABI and fusers

- Derive from the corrected safe-slots full shader, with all current RMS/Q8, norm-scale and GDN gate behavior.
- Keep record words 8..15 as slot indices and keep `slot_ranges` keyed by original buffer/offset/range. This preserves the existing fusion/liveness checks.
- Add a separate host-visible/coherent address table with buffer-device-address support, one uint64 address per slot. Update only after graph synchronization, alongside current pending-descriptor updates. Slot 0 points to the existing 1 GB dummy scratch allocation.
- The `mpc.scratch` push-constant field is unused by current bindless shader bodies; it can point to this address table for the new mode. Keep `mpc.cntaddr` unchanged.
- Use a new .ops mode header parsed by a separate host library to select this behavior automatically. A missing environment toggle must not make a shader interpret the scratch buffer as an address table.
- Retain #views 1 and the slot count for host metadata/fusers at first; the descriptor array may be unused by the new shader. Keep the tape binding.

## Shader requirements

Replace typed `viewN[slot]` references with typed physical buffer references to `address_table[slot]`. Parse nested index brackets, including `view1[tape[base+18]]`. Retain readonly only for actually immutable weight views and coherent read/write semantics for mutable aliases. Validate generated physical-pointer alias decorations and the memory-barrier semantics before running.

Remove only the descriptor `.length()==0xffffffff` dummy probes; preserve genuine local-array length expressions. Choose pointer alignment from the actual largest scalar/component type and guaranteed buffer offset alignment. All ordinary 32-bit scalar/vector views can declare 4-byte alignment; a uint64 address table needs 8-byte alignment. Check all captured offsets before making that promise. Native Vulkan descriptor range robustness is not available through physical pointers, so bounds and inactive-output scratch routing require explicit audit.

Primary alignment sources: [Khronos extension](https://github.com/KhronosGroup/GLSL/blob/main/extensions/ext/GLSL_EXT_buffer_reference.txt), [Vulkan alignment guide](https://docs.vulkan.org/guide/latest/buffer_device_address_alignment.html). These permit smaller alignment than a vector's total byte size, subject to scalar/component and actual-address requirements.

## Gates

SPIR-V validation; conservative 64-group resource/output check; choose larger grid only from actual resources; both 65-frame regressions; dispatch coverage proving FA is actually in the mega kernel; paired throughput with shared-binding control. Do not assume fewer descriptors or fewer pointer words imply better throughput. Wider state rollback, natural-text likelihood and newer production-base qualification remain outstanding before adoption.


## Observed failure and next audit (October22)

The implemented ABI2 derivative passes 9/65-frame checks but faults in repeated llama-bench contexts. Do not rerun before examining lifetime/bounds. `g_mega_addr_cache` is process-global, keyed only by VkBuffer handle, and never invalidated in the captured host. `g_mega.slots` is also process-global, keyed by handle/offset/range. A destroyed/recreated buffer can reuse a handle while its device address changes; the cached physical address and existing slot table entry would then be stale. This is a concrete source-level risk, not yet a demonstrated cause of the faults. Simply bypassing the address helper cache is insufficient if an existing slot key is reused without refreshing its table entry. A fix must track buffer lifetime/generation or compare actual current addresses on use and safely update only after synchronization, covering reused keys as well as new pending slots. Native descriptor paths can also retain stale descriptors across such lifetimes, so establish reset/ownership for all global slot state rather than applying a speculative pointer-only patch. Separate raw-pointer bounds and inactive lanes remain unproven.


The descriptor-only diagnostic in microbench-address-audit-4k/audit.json reproduced actual handle reuse with different device addresses during the full benchmark setup/repeat sequence. Observed old base ffff8001001c0000 is near the earlier fault's low48-bit8001001d8000. The diagnostic uses per-template static maps, so duplicate change lines across shader types are not independent buffer lifetimes. The descriptor shader completes; diagnostic timings include extra address queries and must not be used as comparable performance numbers.

A separate physical-slots-lifetime host calls a creation hook immediately after Vulkan creates each VkBuffer. It invalidates old cached base addresses, removes all old slot-map keys for that handle, and removes pending tuples for the old object. It leaves old descriptor entries/table words unused rather than modifying a table potentially referenced by submitted work. New uses miss the map, fall back and learn new slots at the next graph start. Slot IDs are not reclaimed. This targets demonstrated reuse, but does not prove generic concurrent-context lifetime safety or resolve all possible physical-pointer bounds issues. Shader arithmetic/ABI2 is unchanged.
