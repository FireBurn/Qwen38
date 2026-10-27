# RADV per-process SDMA opt-in investigation

A documented RADV option, `radv_enable_transfer_queue=true`, exposes a dedicated SDMA transfer queue without changing the system driver or another application's settings. See [Mesa's RADV options](https://docs.mesa3d.org/drivers/radv.html). This experiment uses the same private7K RADV/ACO driver as the fusion tests.

## Observed results

- The physical-device query reports no transfer-only family with the option false. With it true, family3 has two queues and transfer/sparse flags, without graphics or compute. The frozen llama.cpp selector chooses the first noncompute transfer family, so the source predicts transfer family3 instead of the previous compute-capable family1.
- With default copy selection (`radv_buffer_meta_path=0`), the captured fresh-process34816float upload at byteoffset42840 still loses46floats in each of its first two full uploads when SDMA exposure is false. All four uploads/readbacks pass when it is true.
- A wider opt-in test passes **144 uploads/readbacks across36fresh processes**: padding offsets0,4,12,42840; float counts32,33,127,128,129,34816,34817,262145,4194305; repeated full copies, split copies and a subsequent full copy. Odd splits include the remainder. No speed is inferred from these tests.
- A transfer-only held client shows positive `drm-engine-dma` time on PCI device `0000:07:00.0` (R9700), reaching19,552,748ns across36samples. All its copies are exact. This proves DMA-engine use in the probe, not a latency improvement. [Linux documents these counters as per-client engine busy time](https://docs.kernel.org/gpu/drm-usage-stats.html).
- Model off/fused/coalesced/coalesced-bounded arms at16workgroups match the canonical complete captured audit with SDMA opt-in true and default copy selection0. All retain34predicted tokens,19drafted,15accepted and SHA-256 `873abacccc270bc1a0669f62ac831dcc14ace252db9f60bbc0006a7c7b84dec2`.

The earlier model fdinfo sample did not record a PCI identifier, so it is not used as R9700 engine-attribution evidence. The held-client test above records that identifier explicitly.

## Interpretation and remaining work

This is a scoped alternative transfer path, **not a general fix for RADV's compute-copy failure**. Default settings were changed only inside experiment subprocess environments. Production and Claude's processes are untouched. The queued fusion performance comparison retains copy2 and its original settings, keeping all arms matched.

SDMA may be relevant to model loading and transfer/compute overlap. Resident decode weights are not uploaded every token, so these results do not establish a token-speed gain. Model checks across more prompts, larger contexts and other queue/copy combinations remain pending before adoption.

## Evidence provenance correction

The first SDMA model runner accidentally retained the previous coalesce16output path. Its outputs were moved intact into this SDMA project. Original compact evidence remains in the published archive; the overwritten original raw logs could not be recovered. The original copy2audit was regenerated successfully, including exact normalized dispatch/barrier comparisons, and the queued performance asset hashes remain unchanged. The corrected SDMA runner requires a fresh output directory. See `model16-provenance-correction.json` and the regenerated proof in the native fusion project.

The wide-copy harness inherited a scope label naming the seed shape. The exported check rows correct that label to describe their explicit per-row counts and offsets; the numeric results are unchanged.
