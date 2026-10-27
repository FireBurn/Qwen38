# Claude notes on the FA LDS phase-reuse plan (2026-10-21 12:30)

Test: full256_mutable_clean.comp plus a dummy shared array that is genuinely written/read across its whole length
(`~/AI/llama-deep/mk/gen/lds_32.comp`), compiled the same way, pipeline stats via GGML_VK_PIPELINE_STATS=megakernel:

| LDS | VGPRs |
| --- | --- |
| 30,720 (control) | 192 |
| 63,488 (+32 KB dummy) | 256 |
| 4,096 (your FA-native split) | 96 |

So the ACO register budget does follow LDS (your hypothesis holds): a ~16 KB FA layout would likely land near 128 VGPRs.
(64 KB and 96 KB dummy variants did not produce stats; an earlier dummy that the compiler shrank to 1 KB changed nothing.)

But your own resource-isolation runs already show lower VGPR/LDS does not buy speed in this schedule:
native-both (96->72 VGPR, 4 KB LDS) 26.98 vs full 27.25 tok/s; 192 workgroups 27.235; limited unrolling 27.30.
My in-kernel clock stats (mk/gen/f256_st) show the loss is barrier wait (~4.3 ms/token, mostly workgroups idling behind
single-workgroup ops and matvec tails), not occupancy: matvec busy time already equals stock's 27.1 ms at 128 WGs.
Upper bounds measured with ops skipped (wrong output): free norms 28.0, free norm+quant+5 small ops 28.5 tok/s, stock 31.5.

Recommendation: do not spend the FA phase rewrite on throughput. It could still be worth it only if a later schedule
needs more than 128 resident workgroups, which nothing measured so far does.
