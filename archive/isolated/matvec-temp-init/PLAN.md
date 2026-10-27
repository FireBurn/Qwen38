# Partial accumulator lifetime experiment

Actual installed-driver ACO live-info trace contains six VGPR main-record-loop phis %37..42, initially undef, with carried values %37005..10. Three pairs are only updated in op26/27/28. Their terminal definitions trace to floating additions in result/bias epilogues, consistent with function-local accumulator arrays partially initialized for dynamic num_rows and passed inout to helpers. These six values are in the live-in set at FA's92VGPR peak. See ../register-pressure/peak-live-vgprs.json and mega-live.txt. This attribution is a hypothesis until a fresh candidate ACO capture shows the phis removed.

Initialize all NUM_ROWS entries of op26/27/28 local temp arrays, instead of only num_rows entries. Active entries retain the same float0 initialization. Iteration, dot, reduction, biases and output stores still use num_rows; inactive rows have no output, no cross-row reduction and no valid arithmetic consumer. No data/slots/scheduling/math change to active rows. This should end previous activation's undefined tail lifetime, reducing pressure across unrelated operator cases.

Three derivatives: reference only, rolledHSV, rolledQK+HSV. Compile only when timing ends. Both9frames64groups/resource first; both65frames at qualified grid; capture actual ACO demand/phis before claiming lifetime repair. Paired micro, then full timing/natural/coverage if a useful gain holds. No adoption merely for lower resources.

## Measured lifetime change

Source-only full accumulator initialization lowers pre-schedulingVGPR91→85. RolledHSV/combined versions reach78 (rolled-loop-only84); final allocation remains96, with25SGPRspills in combined vs24reference. Fresh actual ACO live-info confirms6→0 undef vector phis in the first100header lines and92→79max after-spill demand. This is a verified lifetime reduction, not an occupancy/speed gain. The combined192-grid shortABBA is+0.3244%, longer4K n256/r4 is-0.0483%; no useful end-to-end gain established. Do not adopt for speed.

## Scratch bounds correction

Slope storage originally declared16floats but the cross-subgroup all-masked reduction addresses16+vSGID and16+s (0..3). These are out-of-bounds accesses even though the adjacent IQ storage physically covers their addresses in this Q8KV kernel. Bounds derivative declares20floats at15616 and moves IQ from15680 to15712, disjoint and still within16KB. Actual driver final lowered instructions are byte-identical to original; no performance change inferred. Both9/65prompts pass. A focused three-row Q5_K/Q3_K/Q4_K witness passes16changed-input graphs bit-for-bit to native; last8graphs have zero native operations, proving it exercised mega. Reference promotion still needs natural continuation and actual4K coverage.
