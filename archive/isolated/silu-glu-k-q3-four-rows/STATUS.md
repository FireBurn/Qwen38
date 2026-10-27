# SiLU extension with GLU + FA K prefetch + four-row Q3

Combines the qualified in-place SiLU host with the already qualified GLU/FA/Q3four-row module. Reuses the exact existing shader/SPIR-V/ops and host binary; no source or installed driver change. Both constituents passed operator and9/65frame model correctness separately. Assets pinned in assets.json.

Live first checks run16groups with fusion off/on for short/long prompts, matching existing reference logits. Requires665eligible pairs per9frame check, ensuring the extra SiLU cases are reached. Only after all four prove96VGPR/16KiBLDS/noVGPRspills does the stress runner use192groups/64spare for both65frame changing-input checks, require5985actual fusions and final32graphs fullymega includingFA. Quiet waiter stopped only for this serial private GPU batch and restored in guard finally.

No combined correctness or speed claim until results complete. This new combination is distinct from the already-qualified old-GLUhost four-row bundle and the SiLU-only extension. Existing quiet benchmark scripts/pins are untouched.

All four9frame checks pass bit identical, both prompts fusionoff/on. Fused controls665fusions each, unchanged96VGPR/16KiBLDS/noScratch allocation. Both65frame stress comparisons running.

Prepared final native/reference/old-combination/new-combination quiet comparison with symmetric8runs at4K,n256/r4. Native uses private frozen productionABI.27 binary/core, megaABI.24 paths remain separate, same frozen RADV. Native snapshotmanifest andall9binaries pinned; sourceHEAD plus both source/snapshotfilehashes checked beforequietwait and beforebatch. This measures full stacks, not isolated shader attribution. Queued after exact existing incrementalSiLU coordinator, requiring a new completed2mean/4run summary then successful correctness preflight. Existing quiet queues/assets untouched.

Full combined correctness qualification complete: all four9frame controls and both65frame changing-input sequences bit identical. Both stress runs5985fusions and final32graphs fullymega includingFA. Guard exited0 and resumed quiet portfolio. Same96VGPR/16KiBLDS/noScratch shader allocation, exact existing binaries unchanged. Full-model speed remains unproven.

Full combined native benchmark --check-only succeeded: combined stress proofs, pinned files and native sourceHEAD/sourcebinary/snapshot freshness all match. The three remaining compiler workers arePPID1/single-thread and still consume CPU; fresh read-only sample recorded in compiler-status.json. RecentCPUload has fallen substantially from earlier~99%; compiler-free timing gate still remains unsatisfied. No external processes changed.
