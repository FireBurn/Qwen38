# Attention mismatch isolation

16 process cases completed: native/reference mega, KV256/3328, contiguous/strided separate query inputs, all-zero/causal masks. The two query values and all K/V are identical between layout arms. Native batched/separate outputs exact in every arm. Mega differs from native in every arm; causal masking is not required. Contiguous and strided variants produce byte-identical complete output files within each KV/mask/mode. Thus strided queries and causal mask presence are not sufficient explanations for the original mismatch.

Reference mega batch still falls back to native Flags34 USE_MQ; separate calls run existing Flags2 mega FA. Final32 graphs therefore have32native calls. All values finite; exact driver/backend self-mappings verified;40graphs per process;guard completed and restored original quiet waiter. Source/binary/assets pinned. These are numerical diagnostics with no performance claim. Original model-qualified shaders remain untouched.

Next: qualify actual precision contract of native embedded FA versus generated mega QK/PV and implement the missing USE_MQ path in a separate prototype. Do not silently loosen tolerances or promote these results to full-model MTP correctness.
