# Four-dword compute-copy investigation

## Reproducer and observations

A Q6_K operator case (K=17408, R=3, two columns) initially produced disagreements between native and candidate kernels. A CPU dequantize-and-dot reference and input-scaling checks showed this could not be treated as a candidate arithmetic failure.

A diagnostic then read back the input **before computation**. Its last **46 floats / 184 bytes** were zero rather than the uploaded data. Tensor sizes and offsets were inspected: Q6 weights 42840 bytes at offset 0; input 139264 bytes at offset 42840; bias tensors at 182104 and 182128 in a 182296-byte allocation. No input overlap was found.

A transfer-only reproducer initially passed an offset sweep. Running offset 42840 first exposed the failure. Controlled fresh-process sequence:

| Upload sequence | Result |
|---|---|
| Full 139264-byte upload | 46 tail floats wrong |
| Another full upload, different pattern | Same 46 tail floats wrong |
| Two half uploads, different pattern | Correct |
| Full upload after those smaller copies | Correct |

A warm shader cache did not remove it. Two half uploads in a different diagnostic each lost a tail before the relevant setup was primed. These observations show state/size/sequence dependence; “the first copy only is broken” is too strong.

## Path isolation

The private driver's R9700 queue-family query exposes a graphics/compute family and a separate compute family, but no dedicated SDMA transfer family. Applying the actual host selector chooses family 0 for computation when graphics queues are allowed and family 1 for synchronous copies. The relevant RADV route is therefore compute/CP-DMA selection, not the dedicated SDMA copy route.

The source-defined per-process `radv_buffer_meta_path` overrides were tested:

| Override | Path | Captured repeated-copy test |
|---|---|---|
| 0 | Automatic | Failure reproduced |
| -1 | CP DMA | Passed |
| 1 | One dword / invocation compute | Passed |
| 2 | Two dwords / invocation compute | Passed |
| 4 | Four dwords / invocation compute | Failure reproduced |

These are results for this private driver and reproducer. They are not proof that all four-dword copies, the installed driver, or every model workload fail.

## Partial workgroup lead

Reconstructing the current copy-dispatch formulas, assuming a 256-byte-aligned BO base:

- Destination alignment offset: 8 bytes.
- Start-thread offset: 11.
- Copy threads: 8705; total dispatched threads: 8716.
- Final partial workgroup: 12 threads.
- Valid final partial-workgroup output: **184 bytes**, matching the observed loss.

This is a precise lead, not a root-cause proof. Generated shader bounds, actual command state and GFX12 partial-thread dispatch behavior remain to be isolated.

## Rejected attempted fix

A private RADV experiment flushed buffered pipeline register writes before partial-dispatch register writes, separating duplicate `COMPUTE_NUM_THREAD_*` values into different packets. It built successfully and ran in a matched parent/candidate test. **It reproduced the same corruption and was rejected.** It must not be presented as a fix or used for performance comparisons.

## Impact on optimization evidence

With the two-dword override, native, cached-FA parent, prefix-claim candidate and one-row Q6 candidate agree bit for bit on the affected case. All input snapshots pass; the bias-free scalar CPU reference differs by at most about `8.52e-5`, consistent with floating-point accumulation order.

The operator/model qualification suites were rerun under that override. Comparing all arms under the same override keeps those experiments matched, but an override is not a general driver fix. The failing runs remain in the archive so that their earlier interpretations are not accidentally revived.

## Evidence

See archived directories `mtp-transfer-path-sweep`, `mtp-transfer-repeat-repro`, `mtp-q6-input-diagnostic` and `mtp-copy-partial-registers`, including their structured findings and decision files. Some raw logs and executable reproducers remain local; only files listed in the export manifest are included.

## Dedicated transfer-queue follow-up

Per-process SDMA exposure passes the original captured repro and144copy/readback cases across36fresh processes. A PCI-specific DRM counter confirms R9700 DMA use, and the captured16-workgroup model audit remains canonical with default copy selection. This is an alternative path, not a compute-copy fix or a measured speedup. See the [SDMA evidence and limits](SDMA.md).

## October28 kernel-log audit

A compute-ring timeout matches the process name and timestamp of the old negative default-copy reproducer. The old harness omitted child PIDs, preventing definitive PID attribution. That negative path is now quarantined; it should not be repeated merely to reproduce an already-known byte mismatch. See the [driver audit](../archive/isolated/native-swiglu-q8/driver-audit-20261028.json). Positive SDMA/copy2 results remain scoped observations, not a general driver fix.
