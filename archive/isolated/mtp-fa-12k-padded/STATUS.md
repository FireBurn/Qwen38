#12KiB FA retaining original query padding

Completed numerical/resource/performance study; no promotion. Build75679 terminal0. Only changes from fullyinitialized combined parent: restoreqstride66 andQV1056 allocation/queryslotstride, Koffset8448, mask-reductionoffset11520. No arithmetic,barriers,operator eligibility or output-state scratch changes. Full42ops includingFA retained; SHMEM_STAGING0,Q8KV,HSK256,oneFA-slot scope unchanged.

## Lifetime/range proof

LiveQ0..8448,K8448..11520,maskreduce11520..11536 do not overlap. ExistingWGbarrier immediately before coopMatStore(SfMat) completes Q/Kreads before scores8192..12288 overwrite Qtail8192..8448 and K. AllmaskreadsterminatebeforeK/scorephases via existingread-completion barrier. Probabilities8192..11264 reuse deadscore region onlyafterstagedF16probabilitiesandscore-readbarrier. Vstaging0..8192/Pdisjoint; output0..2048 overwrites deadVonlyafterallVreads and all outputreads finishbefore nextVoverwrite. OriginalquerypaddingrestoredwithoutlargerLDS: actualcompiled12288. Existingglobal64byte per-invocationFAstate ownership unchanged.

## Verification

Guarded21410 terminal0:8armsnative/unpadoff/padoff/padkeep xKV256/3328,F32C1/C2causal,allnative andserialbatch outputs exact; candidatefinal32nofallback. Padoff96VGPR/12KiB/0compiler-scratch;padkeep72/12KiB/0. Unknownshaderfirst16groups.

Guarded64260 terminal0:4causal-future/restore arms and6bias/masked-prefix arms nativeexact. Bias8,finite varyingmaskvalues,128fullymaskedprefix exercises mask storage. NativeKV3328biascase itselfhas slightbatch/serialdifference; candidate preserves each nativeoutput exactly, no universalbatchequality claim.

Guarded39324 terminal0:off16/off192/keep16/keep192/keep256 canonical model34tokens,19drafted15accepted; fulltargetlogits/hidden/draft10 IDs/scorebits nativeexact audit873abacccc270bc1a0669f62ac831dcc14ace252db9f60bbc0006a7c7b84dec2. Private sched-keep driver used throughout (same frozen bundle b571d072...).256launch guarded by72/12KiB capacity320 with64spare and same boundedFAstate range. Head capped192.

## Performance

Guarded73926 terminal0. FocusedFA128copies,sharedKV3328/Q8KV/F32/C2,256groups,samekeep-policy,ABBA:unpad4.0865ms,pad4.0670ms (+.47718%time reduction). Parentdrift.41514%,candidate.09830%; small nearvariation, not an adoption result. Clocktelemetry/last256GPUtimestampwindows retained. Near-cache working set and repeatedquery shape, not standalone modelthroughput.

Quietfull5128arms4modesforward/reverse,all513tokens/279drafted234accepted identical,0buildprocesses,CPU~3%,allquietchecks passed:

| Mode | Mean steady t/s | Paired drift |
| --- | ---: | ---: |
| Unpad,policyoff192 |43.16012|1.17177%|
| Pad,policyoff192 |43.19789|.05985%|
| Unpad,keep256 |43.04321|.50020%|
| Pad,keep256 |42.89758|.17962%|

Padding+.08751%foroff192,-.33832%forkeep256,eachbelow corresponding unpaddedcontrol drift. No model-level gain established. Native/production .27 not interleaved in this layout-only comparison. No claim of beating priornative~49.5t/s or originalmega~43.5. All ownjobs terminal; no system/Claude changes.

Decision: retain as correctness-qualified12KiB layout option, defaultnotpromoted. Querypadding alone doesnot explain remainingnative-to-megagap. Avoid furtherpadding sweeps withoutnew evidence.

Next priority is bigger-picture matched native/mega matrix timing andtraffic attribution: existing isolated tests established resource changes, not why throughputplateaus. Use a single common streamed8matrix C1/C2 harness withactual model-like mixedQ3/Q4/Q5/Q6 weights,beyondcacheworking set,K5120/R17408 andK17408/R5120; compare same wall-time API fornative/originalmega192/newkeep256, alloutputs exact, quietABBA/reverse, clocks/CPU/buildcounts. Do not compare nativefence-instrumentedper-op times with megaGPUtimestamps. Separate matrixstreaming cost from globalbarriers/workqueue overhead before largerFAquerytile/wave32 rewrites.
