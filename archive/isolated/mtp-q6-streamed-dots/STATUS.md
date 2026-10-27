# Q6 streamed independent dot chains

Only Q6 op01/op34 decoded-vector and activation-vector lifetimes changed. Independent dot chains are expressed serially; each retains ascending-component four-FMA order and original final nested scale/FMA expression. All barriers, counter protocols, FA code and42op eligibility remain unchanged in streamed.comp. q6_q45.comp is only a reachability diagnostic.

## Verification

- SPIR-V build and validation completed. Initial build84593 failed only at absent g++ after both shaders successfully validated; client compiled with installed clang++23. build.py now uses that compiler. SPIRV optimizer emitted allocator warnings but terminated successfully; no device crash.
- Initial fast native probe exited0 before external /proc polling observed its driver. Added actual in-client maps check/DRIVER_PATH_OK to avoid timing-dependent proof, then reran guarded batch76193 to terminal0.
- Native,parent,streamed,partial diagnostic tested K5120/R65,K17408/R3,K5120/R4097, both C1 and C2, eight differently initialized matrices, row tails. All12arms native bit exact, batch/serial bit exact, finite, driver/backend maps verified, first16physical groups.
- Q6+Q45 diagnostic96->72VGPR, pre61->49,2KiBLDS,0scratch. Unified shader stays96VGPR/pre83/16KiB/0scratch; code493996->494060 (+64bytes), instructions91157->91169. Source-level lifetime improvement does not imply unified allocation improvement.
- Guarded model/performance session56462 terminal0. Full canonical32requested model at16and192groups:34actualtokens,19drafted/15accepted; all full target logits/hidden, draft10 IDs/score bits native bit exact (audit873abacccc270bc1a0669f62ac831dcc14ace252db9f60bbc0006a7c7b84dec2).
- Quiet512requested ABBA at192groups: parent43.5789784,candidate43.6398057t/s (+0.13958%). Parent drift0.79569%,candidate0.37157%; all513tokens/279drafted234accepted identical.0compiler processes observed; CPU~3%, GPU~3.1GHz. No measurable gain above variation. Same .24 stack/common head, not a fresh .27/native comparison.
- Focused streamed Q6 C1/C2 K5120/R17408,256repeats,192groups, ABBA session86536 terminal0. Parent1369.9863us,candidate1371.7930us (+0.13187%slower), all outputs/serial-batch exact. Environmental telemetry not separately instrumented for micro; do not infer a subpercent bound. Micro script initially had a Python syntax error before launching any GPU process; corrected and rerun terminal0.

Decision: not promoted as a speed improvement. Retain verified Q6 change as an optional component only when combined unified resources actually fall. No grid increase authorized by these results; full shader still96/16KiB. All jobs terminal.

Next: shorten FA eMf array lifetime by computing each row decay and immediately scaling corresponding Of row before next row, preserving row-specific arithmetic, maxima/subgroup semantics, FP16 conversion/multiply and later probability accumulation order. First test standalone FA partition resources/native F32 micro including causal restoration; then integrated/full-model. Both matrix and FA limits must improve together to cross the occupancy threshold. If needed, probe unified noFA with Q6 change to establish whether another nonFA path now becomes limiting, but do not claim partial kernels as requested end state.
