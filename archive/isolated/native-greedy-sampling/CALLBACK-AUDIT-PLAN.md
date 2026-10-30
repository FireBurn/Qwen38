# Raw target callback audit qualification

Prepared source only; no compilation/GPU use during native-default-q3-100 fixed48 session86698 or conditional confirmation. Not used for timing.

After timing is terminal and GPU competition absent, build private runner against pinned aa8 headers and original stock libraries. First run original stock100/default memory/CPU sampling and compare existing binary audit hash, every row header/token/position, tokens and acceptance counters for all five cases530rows. Fail on missing/extra callback captures or layout assumptions. Source assumes exact node name result_output; verify actual pinned model callback naming before build.

Callback asks only for result_output while explicitly target-armed, copies F32 contiguous output rows through backend tensor API, and disarms outside explicit target process. It ignores warmup/draft callbacks and asserts captured rows match requested outputs; callback synchronization and resulting extra transfer make this a correctness-only audit. Never use it to estimate throughput or transfer savings.

Then qualify restricted CPUtemperature-only and backendtemperature-only configurations with identical raw target bits/tokens/counters for the current workload. Inspect accepted GPU chain/output sizes and native supported operators. Do not claim universal equivalence: legacy top-k unstable ordering can alter tied maximum behavior. Any general fast path must preserve legacy ties and nonfinite/bias/suppression/stateful sampling behavior, with explicit fallback where required.

A separate noninstrumented timing experiment needs its own predeclared sample/load rules and direct stock-default control. No shader/core change or performance claim from prepared source.
