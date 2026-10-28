# Q3 padded-weight experiment — current scope

- Native 110-byte blocks are unchanged; alternate copies use 112-byte stride.
- CPU proof: 4096 blocks, all original bytes round-trip, 262144 packed-word checks.
- Diagnostic row3 probe: 720 checks; production C1row1/C2row2 probe: 864 checks. Scalar oracle, native-byte parity, guards, input immutability all pass; no new driver errors.
- GPU repacker: six capped byte-exact cases, including 63/64/65-block tails.
- Two isolated GPU timestamp passes: 96 arms each, including 16 matrix replicas per layout (native working set612761600bytes). Streamed mean block contrasts favour padding in all shapes; clocks are not precisely matched per arm and telemetry has EBUSY errors. Component evidence, not a deployment or full-model speed claim.
- Private model cache is opt-in and only for explicitly immutable WEIGHTS. C1/C2, contiguous/non-view Q3 only; native prefill/fallback buffers retained. Cap8GiB and reserve4GiB. General mutable-weight invalidation is not implemented.
- Model32 audit passes every requested target-logit bit, all tokens and counters: 38 rows, SHA75055a49a5844ad14030f45cb76c11de20a44a6bb0e2db7c1c89a616137eb576.78 cached matrices,3041525760bytes. No hidden-state or internal draft-logit capture.
- Full512 fixed18arm stock/control/pad test: all513tokens/279drafts/234accepts match, no driver errors. All3blocks fail comparability. No supported gain/regression; raw +0.707% versus private control has extremely wide interval.
- Resident-model checks completed: separate-buffer repeat finds no gain; arena screen+1.82% is not independently confirmed versus stock. Coding/math target-logit audits pass exactly. Synchronized per-verification diagnostic also establishes no qualified gain. All GPU jobs are terminal; see STATUS.md and round-handoff.json.

No Claude checkout, production library, original GGUF, desktop setting, clocks or affinity changed. CPU/build load is explicitly authorized and recorded; no CPU quiet gate is used.
