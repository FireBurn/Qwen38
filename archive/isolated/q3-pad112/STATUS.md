# Current Qwen milestone — 2026-10-29

A scoped native-path gain over unmodified stock is established: +3.4302%steady decoding, descriptive95%[+2.2580,+4.6159]%,24fresh512token arms in6matched blocks. No exclusions.38.228→39.542mean tokens/s. Same513tokens/279drafts/234accepts in every run; all audits pass; no new GPU faults.

Qualified uninstrumented candidate: host-fast-guard-v2. Frozen byte-identical library/shaders under qualified-20261029; guarded reproduction wrapper run_q3_pad112_qualified_once.py passes its32token relocation smoke (34matching tokens). It is a private immutable-weight prototype using one3GiB arena, not a deployed production engine or faster mega kernel.

Key evidence: host-profile-runs/20261029T000341Z/analysis.json locates most Q3 MMVQ CPU difference in the selector (2.76vs8.06us). CPU-only getenv2.35–2.56us in copied benchmark environment. Graph-level options and reordered legacy coalescer guard avoid repeated reads. All system libraries/desktop/clocks/affinity unchanged by this work.

Final stock confirmation: guard-v2-matched-stock512/20261029T003112Z. Runtime mapped-libc inode stable; full provenance/telemetry retained. Earlier candidate failures and unqualified screens retained separately. See host-cost-qualification.json.

All GPU jobs from this round are terminal. Goal active: native improvement is a milestone; no faster-than-native mega kernel/FA combination or all-context win established. Preserve qualified snapshot while pursuing additional improvements in new directories.
