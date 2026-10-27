# Row-major P, controlled7KiB variant

Source adapts the layout idea from upstream PR31197 without cached fragments. All42ops retained; float arithmetic and barriers unchanged. Reserved P extent remains3072bytes, although row-major logical footprint is2304, to isolate layout from private scheduler geometry and occupancy. CPU audits prove1024 unique lane writes match consumer tile coordinates,144-byte aligned cooperative row stride, and no score/P overlap.

Build session54702 terminal0: glslc, descriptor alias annotation, spirv-val, spirv-opt, final spirv-val passed. Allocator page warnings also appeared in the successful parent build; no GPU crash inferred from those CPU compiler messages.

Qualification session53175 currently active. Wrapper verifies build manifest, suspends exact childless timing waiter PID284319 by process start identity, runs only the guarded <=16WG test, and resumes the same waiter in finally. InitialKV256 flagoff case native-exact, zero fallback,96allocated/pre58/7168LDS/0scratch. Further cases and performance pending. No high-grid launch authorized by these results alone.

First16 session53175 terminal0: all8 arms native/off/keep/nopre atKV256/3328 native-exact, candidatezero fallback; off96/pre58,keep60/pre58,nopre60/pre58; all7168LDS/0scratch. Original timing waiter resumed after this batch. Wider/causal/model16 wrapper session30688 now active, suspending same childless waiter during sequential guarded qualification. No larger grid or performance claim. All scripts are separate rowmajor7 names; only non-pinned guard allowlist expanded.

Wide16 all16cases and causal16 all4cases now complete/native-exact, no candidate fallback. Fullmodel16 currently running under original session30688. Graduated192/256/320 helper prepared separately with native model bit, wide/causal, hash and60VGPR/7168LDS/0scratch gates, not launched. Cached-fragment build23963 terminal0; its first16 wrapper85295 remains waiting for fullmodel16 success before taking GPU.

Session30688 terminal0: allwide/causal/model16 gates passed. Fullmodel canonicalSHA873abacccc270bc1a0669f62ac831dcc14ace252db9f60bbc0006a7c7b84dec2,34accepted tokens,19drafted/15accepted draft counters, fullbits/nativeexact. Cachedfirst16 session85295 now active; flagoff firstcase96allocated/pre59/7168LDS/0scratch andnative-exact. Graduated wrapper prepared to follow cached terminal success, preserving single GPU job sequence.

Graduated39076 terminal0:192/256/320allcanonicalmodelbits/tokens/counters match native. Qualified arms keep192/keep256/keep320;60VGPR/7168LDS/0scratch asserted each. Comparison scope text inherited mentions off16; actual qualified_arms correctly lists onlythese3arms, while16model evidence is separate. Cached wider65049 now active.
