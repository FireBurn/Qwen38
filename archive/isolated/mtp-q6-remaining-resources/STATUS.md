# Remaining resource audit after Q6 streaming

Build38469 and guarded GPU22288 terminal0. Three diagnostic reachability partitions of verified Q6 streamed shader, first16groups, actual frozen RADV map and native Q4/Q5 C1/C2 output reference exact. Retained Q6 and other nonclient operations are not individually correctness-tested by this batch. Partial/native mixes are never unified performance evidence.

All matrices:72VGPR/pre54/2KiBLDS/code247120. All exceptFA:96/pre65/2KiB/code456144. All exceptFAandQ6:96/pre65/2KiB/code434052. All0scratch. The Q6 component succeeds for the entire matrix group, but remaining nonmatrix/control-flow paths independently still reach96, even with bothFAandQ6 absent. Therefore FA resource reduction alone will not guarantee a lower-resource unified kernel. Next isolate nonmatrix families (GDN,RoPE,norm/control etc.) rather than assume matrices/FA are the only ceilings. No speed claim/adoption, no GPU job active from this batch.
