# BF16 delayed pair with bias

Captured audit:48pairs, same5120-element activation input,48rows each, BF16 matrices491520bytes, same192-byte raw destination. Two RMS ops and a48-element add lie between them. Raw first output is consumed only by that add before the second projection overwrites it. The two outputs cannot be preserved independently at the original raw location.

New host pass matches exact frozen13-word matvec parameters and29-word add parameters. It accepts only the pattern BF16/RMS/RMS/ADD/BF16 ignoring grid barriers, checks all relevant ranges for overlap, and requires same input/output slot IDs. Fusion runs after existing passes so existing liveness scans do not see the extra compound outputs. A #bf16_pair1 header plus opt-in flag is required.

First record doubles grid24->48tasks. Each subgroup retains unchanged dot-product arithmetic for one projection: tasks0..23 use original matrix and existing bias epilogue into ADD's output; tasks24..47 use second matrix, no bias, into raw output. Extra slots18secondmatrix/19secondoutput; flag0x1000. Original input, norm tasks and all downstream operations stay. The original ADD and second matvec records are removed, with redundant grid barriers compacted. No two-accumulator dot-product rewrite.

Validation/timing pending. No production sources changed.
