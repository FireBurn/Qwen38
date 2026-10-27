# Guarded fixed-shape Q3 experiment

Read-only review of Claude conversation 7f8aaebd-dca1-49ae-ac5b-504e54a7012b finds last relevant kernel result October21 17:21: n5 shared binding depth0 has no useful gain, stock RMS/Q8 reverted; subsequent changes concern production server speculation and long-context native attention. No later mega win found there.

Candidate clones op27 helper functions with all dimension/stride/broadcast fields constant for the sole Q3 tuple in matvec-shape-audit.json. Fusion flags and descriptor slots remain dynamic. The wrapper checks every constant field before calling the clone, otherwise calls the original. No host ABI/capability change required. The accumulation while loop retains DontUnroll; instruction arithmetic and reduction order are unchanged. Source guards do not assert a universal model shape.

Both9 and both65-frame prompts pass bit-for-bit. Driver96VGPR/24SGPR spills/16KB LDS/code263404/preVGPR93 versus reference241132/pre91. No occupancy increase qualified. Timing determines whether reduced indexing work outweighs larger code/guard cost. No promotion before paired timing, natural continuation and coverage gates.
