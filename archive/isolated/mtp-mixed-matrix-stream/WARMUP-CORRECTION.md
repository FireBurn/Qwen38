# Mixed matrix timing correction

V1 short warmup contained a GPU clock ramp. V2 counted lazy pipeline compilation toward its two second warm duration: the keep arm completed only 64 pairs in 3.954 seconds, versus 831 native and 695 original pairs in about two seconds. The keep measurement failed the existing clock stability gate. Neither partial experiment supports a performance claim.

V3 retains both versions and their evidence. It first executes 64 batch/serial pairs and synchronizes, then warms only the selected timing graph for at least three seconds, synchronizing every 16 executions. Compilation and this separate warmup remain outside measurement. Timing and quiet/clock gates are unchanged. Shader, backend, and driver are unchanged. All GPU jobs use the existing exclusive guard.

V3 qualification and benchmark evidence are written separately under settled3-first16 and settled3-bench. Performance results require byte-exact native outputs and the existing settled-clock and quiet-environment gates.

Source audit: frozen ggml-vulkan.cpp lines 10724 onward confirm quantized activation reuse is a single last-pipeline/last-tensor cache backed by prealloc_y. Alternating distinct inputs can force requantization. This is an interpretation constraint for the independent versus chain benchmark; observed host sync call counts are not measured barrier latency.
