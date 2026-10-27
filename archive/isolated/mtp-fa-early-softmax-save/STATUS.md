# Save FA softmax state before PV

Build1034 and guarded first16batch72906 terminal0. Existing exactF32 Lf/Mf stores moved from KViteration end to just after complete probability formation; no arithmetic or memory-operation count change. Original barriers, disjoint per-invocation scratch records,12KiBLDS and integrated42op eligibility retained. Parent is verifiedGDN-late/Q6/12KiB explicitFAstate module.

Eight arms native,parent,fullcandidate,FA-only xKV256/3328, causalC1/C2,F32reference. All native fullbinary and batch/serial outputs exact; candidates zero nativeFA/reduce dispatches in last32graphs; driver/backend verified. No newly executed192launch/fullmodel/causal-perturbation qualification or performance claim for this variant.

Resource hypothesis insufficient: full96VGPR/pre75/12KiB/0compiler-scratch/code495868; FA-only96/pre66/12KiB/code43612. Parentfullpre76; previous compactFA-onlypre67. Early-store source placement reduces reportedpre by1, not the8initially hoped, and does not lower final allocation. Therefore no long benchmark/promotion; negative resource gate is sufficient to stop testing this candidate as a speed improvement. All jobs terminal.

Next inspect outerloop accumulatorphis from ../mtp-fa-liveinfo/STATUS.md, then revisit actual FA live peak. Reducing carried scratch SSA values may remove pressure without extra memory traffic. Existing blanket nosched regressions still apply; no reason to repeat them.
