# Subsequent native greedy/sampling leads (not implemented/tested)

Pinned aa8 .7 source inspection after transfer observer:

- Target CLI currently uses --temp0 and default sampler chain, only DRAFT --spec-draft-backend-sampling is enabled. Target --backend-sampling exists but defaultsdisabled (common/arg.cpp).
- Common default chain still constructs enabled rank/filter stages before temperature0/greedy. Without active grammar/reasoning budgets/penalties/nonzeroXTC etc, monotonic top-k/top-p/min-p filtering should retain the maximum; testing a temperature-only target chain could remove redundant CPU filtering. Must prove exact greedy tokens/counters, tie behavior, unchanged suppress/logit-bias handling and applicability; not a blanket chain simplification.
- Native temp<=0 backend code computesargmax, gathers chosen candidates/logit, so output can be one item. Common::set_logits first rebuilds sampled candidate arrays before accepting backend-selected token; inspect actual chain/outputcounts rather than assuming CLI alone removes full arrays.
- Observer sees370asyncgetrequests/151,557,920requestedbytes per128reqdecode. Much appears to be raw target logits; measure named bytes/actualbackendchain before attributing/saving them. Existing backendgreedy samples do not necessarily suppress all logits/candidate outputs.
- Potential smaller shader: exact hierarchical argmax + chosenvalue/ID gather, or output-head matvec+partialmax thenfinalreduce, only if measured current native GPU reduction is underparallelized and on criticalpath. Native Q8 row arithmetic/tie ordering must stay exact; added VGPR/LDS/dispatch costs may negate it. Existing .24 bounded-output-head project is relevant but cannot be blindly ported to .27/default environment.

No compiler/GPU work during current mapped48A/B. First correct the baseline to unmodified stock/native allocation defaults; then predeclare isolated CPUchain/backend-sampling controls before new kernels. Full target-bit audit needs a proper graph-eval callback if backend sampling intentionally omits raw logits; never hash uninitialized/stale sampling buffers. No performance or implementation claim from this note.
