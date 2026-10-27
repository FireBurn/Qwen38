# Reference provenance correction — 2026-10-25

The repeated 213-record checks in the occupancy, dispatch-coalescing and tape-replay investigations compare against `isolated/mtp-q4/large-grid-audit/checks.json`, mode `q4`. That is a saved **mega-kernel baseline**, not an independent native execution.

The earlier 30-record proof `mtp-q4/logits-audit/logits-comparison.json` compares the q4 mega module with its preceding mega parent. It does not establish native logit/hidden equivalence. Historical token/acceptance checks and per-operator native byte comparisons are separate evidence and must not be substituted for full-model native float equivalence.

Any preceding description of those specific 213-record results as "native" was too strong. They establish preservation of the saved mega baseline only. The record comparisons remain valid; their reference was mischaracterized.

The current larger-prompt test performs a genuine native execution by removing GGML_VK_MEGA. Its 195 logits/hidden records differ from the parent mega output. Parent, replay, native-FA fallback, no optional fusers, and all-grid-barriers variants produce the identical parent result. This separates the observed difference from the new replay implementation. It does not alone establish unacceptable model quality: alternate FP reduction orders may produce numerical differences and change speculative acceptance. Native equivalence, accuracy tolerance and task quality must be assessed explicitly.

A strict individual-operation verifier currently reports RMS differences. The extracted native RMS SPIR-V has LocalSize512 and no subgroup FAdd; the mega source uses 256 logical lanes and two-stage subgroup FAdd. This is a concrete source of floating-point order differences. Do not assume it explains every full-model difference until isolated and tested.

Performance adoption remains blocked by the outstanding numerical qualification. No production or installed change has been made.
