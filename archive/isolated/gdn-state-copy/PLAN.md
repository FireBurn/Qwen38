# GDN state copy bypass

Private bounds-reference derivative. Captured final 4K graph has 48 GDN/projection/contiguous-copy sequences. Each copy reads 3 MiB of final state from the packed GDN output and writes a separate persistent destination. All 48 destinations are disjoint from all producer inputs/outputs and intervening projection descriptors. Capture audit: capture-audit.json.

First version preserves the packed state stores, adds the destination store from the same computed register, and deletes the copy. Saves 144 MiB of reads/token plus copy work; does not claim the old packed state is dead or remove its stores. Exact arithmetic/reduction/snapshots unchanged. This is an incremental alternative to eventually routing state directly.

Host requires capability header version1, bindless, verify0, opt-in flag, no GDN-QK experiment; exact GDN kernel identifier, H48/n_tokens1/n_seqs1/K1, original flags only sigmoid; one intervening unmodified matvec; exact 30-word contiguous-copy parameters; copy source exactly packed output + s_off*4 with exact state bytes and output bounds; destination exact state byte count and disjoint from all GDN and intervening matvec slots. Barriers kept, only redundant adjacent barriers compacted. Generic path retained for every rejected shape. New destination slot18, flag bit2. Shader default unset retains prior behavior. No new record-relative offsets.

No grid increase. First64 groups checks and actual pipeline stats; require96VGPR/16KB or better and no VGPR spill before192. Then9/65frame parity on both prompts and matching fusion counts; paired micro on same host. Full timing/likelihood/coverage needed only if promising. Do not change CURRENT or production on compilation/parity alone.

## Result

Both9/65prompts exact,96VGPR/24SGPRspills/zeroVGPRspill/16KB. Micro effectively flat/slower; not adopted. See evidence.json. All GPU jobs terminal. No original packed stores removed.
