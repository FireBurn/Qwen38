# Two-query FA extension

Extend operator-only all-matvec module, sharing existing op22 FA functions through a uniform USE_MQ boolean selected by dispatch IDs22(false)/36(true). Add only exact Flags34 pipeline alias, reusing original descriptors and LDS. Original one-query dispatch sets false explicitly. Native source already supplies row/head/mask/output indexing for USE_MQ; parent source retains those branches but constant-folded them away. No new arithmetic, no activation requantization.

Qualification requires explicit F32 accumulator contract (fixed mega QK precision), first <=16physical groups, native-F32/batch/serial byte equality, no final native fallback, resource inspection. Broad shape/mask/layout/changing-input tests and model attention/cache/MTP/controller validation remain before promotion. Dynamic branching/code-size/register effects need local/full timing; no speed claim from launch-count reduction alone.
