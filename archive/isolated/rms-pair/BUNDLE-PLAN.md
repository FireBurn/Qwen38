# Bundle independent projection and RMS tasks

The previous BF16 pair fusion retains two independent RMS records between its original projections. The existing range guards already prove the pair's inputs and final outputs disjoint from both RMS writes and sources. The two RMS records are also independent of each other (audit.json). This permits concurrency within one record, rather than only joining RMS grids sequentially.

## Proposed scheduling

Use a separate shader/host capability and opt-in flag. Run the host pass after existing BF16-pair fusion and require the immediately following two non-barrier records to be the known 16-group/128-column RMS shape, matching params, post-scale/bias and no incompatible flags. Recheck all cross reads/writes, including projection second matrix and output, bias input and sum output. Keep descriptor slot IDs and all arithmetic.

Keep the RMS records in the tape as parameter blocks. Store their relative record offsets in BF16 record words20/21 and the second RMS offset in22. Flag0x4000 denotes the bundle (BF16 pair itself uses0x1000). First16 physical groups call the unchanged first RMS wrapper with logical group0..15 and logical grid16; next16 call the second RMS wrapper. Remaining physical groups run the existing BF16 pair's guided wave queue. Routing is uniform across each whole physical workgroup: RMS local barriers must never be entered by only some of its waves.

Forward-declare run_op07_ before the BF16 wrapper; add routing at the very start of run_op06_, before its normal parameters are loaded. This avoids another duplicated matvec/RMS implementation. After this wrapper and its existing workgroup barrier, the main record loop skips through the second RMS record for flagged op6 records. The next grid barrier then waits for all three independent outputs, using the ordinary incrementing barrier epoch. The skipped intermediate grid barriers do not increment the epoch. Unused counter slots may remain; the active BF16 queue retains its original record counter index. Other record shapes stay on the current sequential path.

No subgroup-only routing for RMS. No raw-address mode. Safe LS32 cache writer and full FA remain untouched. Audit capability/range guards, SPIR-V memory semantics, whole-workgroup control flow and counter bounds, then conservative64-grid resources/output check before choosing192. Both65-frame prompts, real-token continuation, actual dispatch coverage, then paired micro/full timing against the existing BF16-pair reference are required. A nominal reduction in barriers is not a speed claim.

Potential benefit: overlap tiny BF16 projection work with independent RMS work and remove two grid-wide synchronization phases. Risks: fewer groups available to the projection queue, extra dispatch branches/code size/register pressure, or a scheduler bookkeeping mistake. If the model checks fail or measured speed regresses, preserve the current reference.
