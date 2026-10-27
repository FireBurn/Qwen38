# Experimental single-submit decode host

The ordinary host backend cuts graphs by a 100-node limit, a flop threshold, and an early-ready fence. Those cuts also flush the persistent tape: the corrected full shader still executes in 19 segments per decode graph.

This independent library adds opt-in `GGML_VK_MEGA_SINGLE_SUBMIT=1`. It bypasses those cuts only when a megakernel is active and every GDN operation in the graph has one token and one sequence. A graph without GDN does not qualify. The shader, descriptor contents, barriers, weights, and cache precision are unchanged. Prefill and multi-token graphs retain normal scheduling.

Prepared by `../prepare_single_submit.py`, built by `build.py`, and selected with process-local `LD_LIBRARY_PATH` beginning with this directory's `bin/`. It does not replace the default isolated Vulkan library or any Claude binary.

Validation script: `../run_single_submit_checks.py`. Building alone is not a correctness or speed pass. Tests must run after the current GPU benchmark finishes.
