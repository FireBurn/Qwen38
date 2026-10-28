# Production .27 native quantizer / Q3 operator port

Eight focused operator arms pass: C1/C2 × fourquantizer/Q3on-offmasks. All output bytes equal their own production control. Actual dispatch counters confirm enabled shaders replace original quantizer/Q3dispatches; they are not merely loaded/compiled. No newtargetdriverfaults. No model or speed qualification yet, and no production SwiGLU fusion port.

Read-only sourceHEADaa8ab0504deda8ef55958aa2c7ccdee3eab924ca fromClaude's prodtree matches the preserved .27/.7 production libraries. build.py copies original shader/buffer objects and headers into this own experiment and compiles only a new own main Vulkan translation unit. Inputs pinned/verified unchanged through build; original source/build objects never written. Shared device/context/headerlayouts unchanged across translationunits.

The new per-device module map belongs only to the main.cpp, retains SPIR-V for process lifetime, and is populated under its own mutex from the existing compile-locked lazywalk. Original lazyfactory compiles after unlocking, avoiding the prior synchronous-init deadlock. No quantizer cache/geometry/activation policy or barrierchanges. Both replacements off bydefault and gated to testedAMDdevice0x7551; quantizerwave64+shuffle/fullsubgroup support additionallyrequired. Q3requiresall3modules orfallsback. This is a private prototype, not installed code or an upstream patch.

host/ is the default-off release-style port without dispatch counting. validation-host/ adds a wrapper around main.cpp dispatch calls and atomiccounts per pushconstant-type instantiation. All counter lines are summed; this validationhost is not for performance comparison. Otherobjectdefinitions remainunchanged. build_validation.py also rebuilds the existing four-quantclient against actual .27/.7headers/libs, avoiding cross-version ABI/enumeration assumptions.

The focused workload uses64SwiGLUpairs feeding Q3_K/Q4_K/Q5_K/Q4_0 consumers,4patterns,3outputrows,C1/C2. Only quantizer/Q3modules change. C1nativeoutputSHA5f2dc61c293632b3fa70be8919af256fa1b55a60e909e9b151a4ce36cdb07f67 differs from old.24control; C2SHA9f32c0055a53a782585d33ef6289df2a674d133877007f00c8645c5de731139f matches it. This is expected to require its own same-stack controls; no cross-versionnumericalequivalence asserted. Outputbytes within eachcolumnsetting areexact acrossall4masks. Warmupiterationcounts differ; loggedus_per_graph are not qualified speed measurements.

operators/checks.json recordsprocessIDs,actualdispatchcounts,outputhashes andnewdriverchecks; comparison.json theboundedclaim. Runtime uses thepreserved .27/.7stocklibraries andsameprivate7kMesa,copy2,SDMAoff. StockMMVQ/activationheuristics retained; old .24MEGA/head flags absent. AllGPUjobs serialthroughprivateguard andexactownchildlessquietwaiter paused/resumed.

Next: productionMTPmodel controls withcomplete requestedtargetlogitcapture andtoken/counter checks, distinguish that fromoldbackend'sfulltargethidden/draftscoreaudit. Thenlongerprompts/currentproductionfusionport andmatchedquiettiming. Existingperformancequeuesremainlive,waitinghighCPUload; nofastermodel/mega claim.

## Production model target-logit audit passed

build_model_audit.py derives an ownrunner from the preserved .27/.7speculative runner, withoutcoreedits. Aftereach runner-owned target llama_process() call it serializes batchmetadata andallrequestedfull-vocabulary targetlogitrows; checksreturnstatus,non-nullrows,writes/flush/close. Extraexactcorepathmapping marker verifiesstocklibllama.so.0.7.0 alongsidebackend/driver markers. Draftinternalprocesscalls,targethidden anddraftscorebits are not captured; do not call this the oldfulltarget/draftaudit.

model32/ fouron/offarms allmatch targetlogitauditSHA75055a49a5844ad14030f45cb76c11de20a44a6bb0e2db7c1c89a616137eb576,37745416bytes,38fullvocabrows across20targetbatches.34predicted/19drafted/15accepted andall34tokenIDs identical. Actual4738quantizer/1560Q3dispatch substitutions confirmed. Decoderactivationheuristicsunchanged; no .24privatehead flags or fusion. No newtargetdriverfaults. Losslessauditgzipverifiedbeforeremoving4identicalrawcopies.

stock-model32/ independently runs the exactsameauditrunner against unmodifiedproductionbackend .27, samecore/driver/flags. Completeauditbytes,tokens/counters match hookeddefault-offcontrol andallcandidates. Historical17tokenproductionprefixalso matches. Thus theobservednumericalparity is anchoredto actualunmodifiedproductionlibraries,notonlyto ournewhost. No dispatchcounters expectedinunmodifiedstocklibrary.

Theprivate release-style host remains distinct from validation-host counters and from modelaudit instrumentation; timing mustuseunmodifiedbenchmarkrunnerandreleasestylehost. Model capture introduces synchronization andisnot timing evidence. Longerprompts/contexts,productionfusionport,completehidden/draftauditcoverage andquietperformance remainpending. No faster-than-baseclaim.
