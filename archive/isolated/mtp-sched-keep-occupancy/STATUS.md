# Private ACO occupancy-preserving scheduling experiment

Complete first study, defaultoff and not promoted. Mesa AGENTS read before edits: no GitLab actions,comments/commits or restricted-driver edits. New source fork only3AMD files differ; no new code comments. Existing source/build/driver snapshots untouched. No priority/clock/affinity changes. Build28488 terminal0, ThinLTO/j2 private AMD-only RADV. Frozen newdriverSHA b571d072f9250e33a237c9b0744ee9f2aa7c72fe90e77099fad0421cedb4e375. Fresh bundle links systemlibdisplay-info4; SPIRVTools privately copied, remaining dependencies system. Noinstalleddriver changed.

FlagACO_DEBUG=sched-keep-occupancy-12k (newcodegen bit0x4000,not excludedfrompipelinekey) affects onlyGFX12,wave64,256thread,12288byteLDS pipelines. Chooses target_waves from pre-scheduling num_waves rather than trading waves for register headroom. All pre/post scheduling passes execute. No semantic claim that geometry uniquely identifies mega: it is explicitly a geometry filter. Source/patch hashes inpatch-manifest.json.

## Resource and numerical gates

Guarded28927 terminal0:24matrix arms Q3/Q4/Q5/Q40,C1/C2,K5120/R65,4changinginputs/3biasmodes,flagoff/keep/no_pre. Nativeoldreference byte exact. Same-newdriver off reproduces olddriver fullshaderHash2117641831,Code495400,91338instructions,96VGPR/pre67/12KiB/0compiler-scratch. Keep uses72VGPR/pre67/12KiB/0,Code497512,91849instructions,Hash3151712973; no_pre control72but500024bytes/92729instructions. New policy retains useful scheduling transformations compared with disabling pass, but resources/instructioncounts alone do not prove speed.

Guarded76775 terminal0:8FAarmsnative/off/keep/no_pre xKV256/3328,F32causalC1/C2 allnative bit exact, candidateFA/reduce final32nofallback. Strong backend/actualdriver maps checked, private driver library hashes pinned.

Guarded46641 terminal0:off16/off192/keep16/keep192/keep256 modelcanonical34tokens/19drafted15accepted; all targetlogits/hidden/draft10IDs/scorebits nativeexact audit873abacccc270bc1a0669f62ac831dcc14ace252db9f60bbc0006a7c7b84dec2. 256uses same72VGPR/12KiB, source-derivedcapacity320 leaves64spare; same bounded64byte/invocation state within1GiB. Head capped192. No larger gridqualified.

## Quiet full512 comparison

Guarded70920 terminal0.8arms4modesforward/reverse,same newdriver/common .24 core/backend/boundedhead. All513tokens/279drafted234accepted identical.0compileprocesses,CPU~3%,GPU~3.0-3.1GHz,allquietguardspassed.

| Mode | Mean steady t/s | Paired drift |
| --- | ---: | ---: |
| Native body/commonhead |49.48974|0.9537%|
| Same shaderflagoff192 |43.11449|0.1066%|
| Keepoccupancy192 |42.90458|0.7969%|
| Keepoccupancy256 |43.18238|0.1733%|

Keep256+.15748%vsoff192,withinits.1733%drift; no demonstrated gain. Still12.7448%slower than matchednativebody. Keep192-.48685%vsoff192,also belowitsdrift. Native baseline here is .24commonboundedhead, not freshproduction.27. Previous no_pre25640.5757 from prior quietsession was materially worse, but cross-session comparison is not an interleaved attribution. No need further reruns ofthese exactmodes without newhypothesis. Defaultflagoff retained; noadoption.

## Next concrete layout lead

The12KiB family removed nativeQpadding to fit Q8KiB+score4KiB. It can potentially retain originalqstride66/QV1056(8448bytes) while K remains8448..11520, score/P start8192. Score overlaps onlyQtail8192..8448 andK after existingWGbarrier before coopMatStore(SfMat), so liveQ/K are not simultaneously overwritten. Move4floatmask-reduction storage from8192 to11520..11536 to avoid corrupting liveQtail beforeKQ. P8192..11264,Vstage0..8192,output0..2048 retain existinglifetimebarriers. Maxextent still12288. This is not implemented: prove allscalar/vectoraccessranges, microbias/maskedprefix/causalrestore, resources and fullmodel, then focusedFA and fullbench. Restoring original query padding may remove bank-conflict cost without sacrificing12KiB; not a speed claim.

Broader occupancy lead remains logicalquerymicrotiles/paddedWMMA16 plus narrowerPVstaging to reach8KiBLDS andsmalleractualVGPR. Major geometry/mask/GQA/state rewrite required; do not enable wave32or shrinkBr blindly. Current result is useful compiler capability, not achievement of faster-than-nativegoal. All ownGPU/build jobs terminal.
