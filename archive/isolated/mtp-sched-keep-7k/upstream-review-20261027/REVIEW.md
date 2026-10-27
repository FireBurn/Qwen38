# Upstream candidate review, 2026-10-27

Downloaded patches are evidence snapshots only; neither was applied. Existing performance portfolio remains unchanged.

## PR 31197: CM1 row-major P and fragment reuse

https://github.com/ggml-org/llama.cpp/pull/31197
Draft, one commit ad0f08c7d276a34e7b7b7a42e1816983e3f276e0. Snapshot SHA256 7268febfd732fd458b01d627717ee69782a49f1a6e740c75909343bfc139eaa5.

Changes P shared layout from Bc*(Br/4+2) f16vec4 to Br*(Bc+8) half scalars, changes producer stores, and hoists Bc/MatBc probability fragments outside HSV tile loop. Host shared-memory estimate changes accordingly. This is a relevant algorithmic idea, not a drop-in patch for our aliased persistent shader.

Current rowwise.comp retains column-major P at LDS offset4096 with384 f16vec4 entries; coopMatLoad(PMat,...) is inside PV slicing at line3413. New row-major P for Br16/Bc64 would occupy16*72*2=2304 bytes versus existing3072 bytes. Raw byte saving768 does not itself establish a lower hardware LDS allocation or occupancy improvement. Region/address/barrier audits must be regenerated for a new layout. Caching fragments may increase VGPR allocation above60 and erase occupancy gains; measure resources before any higher-grid launch. Preserve current producer rounding and per-row L/M arithmetic; validate causal tails, prefix/bias, KV3328, and canonical full-model bit checks. Compare row-major-only and row-major+cached fragments separately to distinguish layout from register effects. Timing at longer context is required because short decoding underweights FA.

## PR 31196: Q8_0 weight reuse for9..16 columns

https://github.com/ggml-org/llama.cpp/pull/31196
Draft, snapshot SHA256 de799549382fb1bcd1b1abc73f21c233337fc1e56c97f0bded120e432ac91462.

Adds AMD-only wider MMVQ gate and A-reuse shader for Q8_0 with9..16 columns; preserves src1 precision eligibility. Author measurements are W7800/RADV26.0.8, not this R9700/private stack. Current C1/C2 dense decode does not enter this column range; target blocks are chiefly Q3/Q4/Q5/Q6. Model has large Q8 output/embedding tensors, but embedding lookup is not proof of MMVQ work. Relevant if draft breadth changes or graph inventory shows9..16-column Q8 operations. Do not claim a current decode gain from the upstream reported numbers.

Priority: measure already-qualified60VGPR kernel first; then isolate row-major P layout on that source, qualify <=16 workgroups, and only retain fragment caching if resources and full-model performance support it.
