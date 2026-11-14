# What may transfer to Qwen4

Reviewed 14 November 2026. Qwen describes [Qwen3.8-Flash-Next](https://huggingface.co/Qwen/Qwen3.8-Flash-Next) as an experimental architecture preview for Qwen4. Its published MoE model uses Gated DeltaNet, Qwen Sparse Attention, gated residual streams and n-gram embeddings. Those features are evidence about the preview, not a guarantee that every final Qwen4 checkpoint has the same shapes, operators, supported quantizations or memory layout.

| Prior work | Transfer outlook | What must be redone |
| --- | --- | --- |
| R9700 Vulkan/driver constraints, safeguards, correctness and matched-load tools | High: generally useful across models on this stack | Revalidate against new runtime, driver and graph; do not treat historical throughput as a new baseline |
| Gated DeltaNet and recurrent-state investigations | Potentially useful: the preview retains Gated DeltaNet | Check head shapes, recurrence, fusion, state layout and rollback on the actual checkpoint |
| Q3/Q4/Q5/Q6 and Q8 activation operations | Potentially useful if the same GGUF quantization and backend paths are used | Reprofile matrix shapes, quantization, graph eligibility and native performance |
| SwiGLU-to-Q8 prototype | Conditional: concept may apply to compatible FFN operations | The current prototype explicitly requires 17,408 elements and five columns; inspect the new graph, adapt guards/shader, retest outputs and benchmark. Current synthetic operator pass is not full-model or speed qualification |
| Flash Attention and mega-kernel ideas | Partial: generic numerical and scheduling lessons transfer | Qwen Sparse Attention adds an indexer and selected blocks; old dense-attention or whole-layer assumptions do not establish correctness or speed |
| DFlash and speculative width results | Methodology transfers; checkpoint compatibility and best width do not | Find a compatible draft or supported MTP, test acceptance/rollback and sampling, then remeasure. Three width studies were inconclusive under changing load |
| Prior wider greedy argmax improvement | Conditional, limited to the measured old stack and greedy path | Verify vocabulary, sampler path, runtime and independent end-to-end speed for the new workload; it is not evidence for stochastic Qwen4 sampling |

A [llama.cpp issue](https://github.com/ggml-org/llama.cpp/issues/31072) discusses possible Qwen4-27B shapes inferred from an Intel kernel PR. It suggests similarities in hidden size and Gated DeltaNet, but also different residual connections and a potentially different FFN width. This is third-party inference, not an official Qwen4-27B model specification; do not hard-code it as fact. The current five-column fusion's fixed width and the existing DFlash draft are therefore not assumed compatible.

When suitable weights and runtime support exist, capture the real execution graph and populated context first, verify model output and state handling, identify shapes and bottlenecks, then port only matching guards and remeasure against the new stock baseline. No Qwen4 speedup or compatibility has yet been demonstrated here.
