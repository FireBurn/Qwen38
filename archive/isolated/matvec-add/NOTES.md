# Matvec/add epilogue experiment

The full-tape audit has 32 adjacent simple add opportunities. The implemented host pass uses the existing bias epilogue, redirects the matvec output, and removes the add only after proving its raw output dead in the current segment. It rejects overlapping inputs, requires the frozen contiguous 5120-element shape and one batch with base-workgroup Y zero, and bounds future overwrite proof by logical write size. An opt-in flag leaves normal behavior intact.

Built separately. Both short checks and both 65-frame regressions pass bit-identically. Runtime finds only 14 pairs over eight steps, unlike the full-tape upper opportunity count. No speed claim or deployment. No GPU run remains active.

Next: preserving both raw matvec output and residual sum in the existing epilogue may unlock more pairs without discarding live values. Use a new host/shader pair; retaining the raw output is necessary, not permission to relax the current liveness proof. Measure resource allocation before choosing a persistent grid.
