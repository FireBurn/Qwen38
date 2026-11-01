# Buffered-output reconstruction (CPU only)

The failed stock-control output is 15,360 bytes. It contains 579 complete records through `(1025, 5, 4)` and the first four bytes of the next header. The checker writes a 16-byte header and then 4 bytes per row only after GPU computation, synchronization and readback complete.

A separate CPU-only program using the same compiler, C++ runtime, output filesystem and `fwrite` call sizes reproduces the output-buffer progression without opening Vulkan. Its output file remains 15,360 bytes after completed records 580 through 618. In this reconstruction those records run from `(1025, 5, 5)` through `(2047, 5, 1)`; the next record would be `(2047, 5, 2)`. If the failed process used identical stdio buffering and did not flush or write the output differently, its failure during a subsequent readback would fall between cases immediately after records 580 and 618. This is a conditional narrowing, not an exact case attribution: the failed process was not traced, its actual in-memory stream buffer was lost, and runtime/environment differences could change buffering. No failing shape, shader or root cause has been established.

The new single-case diagnostic emits a flushed case marker; it has not run on the GPU. The private GPU-fault hold remains active. No historical or current failed attempt is combined with passing measurements.
