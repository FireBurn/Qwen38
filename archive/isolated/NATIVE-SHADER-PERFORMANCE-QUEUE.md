# Native shader timing queue

The native quantizer shuffle and native Q3 correction now have a dedicated full512 timing workflow, queued behind the existing shuffle-fusion workflow. No timing has started and no speed result is available.

Live wrapper initially PID1223174, original execution session82724. Check its actual /proc identity before any action; do not infer liveness from this note. Its predecessor is exactPID888785/start_ticks5143700 and must produce successful workflow-complete.json. The existing parentPID867089 and childquietwaiter867095 are unchanged.

run_native_shader_performance_after_shuffle.py pins tested shader modules, hosts, core, driver, modelbenchmark runner, timing script and synthetic telemetry test result. It requires successful predecessor completion, then enters the existing private serialization guard. Failure or new driver faults stop the workflow.

run_native_shader_full512.py waits90seconds withCPUbusy<20%, no compiler and no competing harness. Eight512requested-token arms run forward/reverse: quantizer off,on andQ3off,on. Each candidate is compared only against its own identical host control. Shared frozen core/private7kdriver, boundedhead192groups, copy2 andSDMAoff are constant. All generated tokens andMTPcounters mustmatch. Original warm/steady and total generation timing are separatelyreported.

Sensor errors are retained even when idle. Any sensor error duringsteadygeneration or telemetry worker failure invalidatesanarm. Existingminimum8GPUactiveclocksamples/settling limits, zero backgroundbuilds and steadyCPUload gates are retained. test_native_shader_telemetry.py executes theactualmonitorfunction andvalidityexpressionAST withsyntheticidle/timedsensorfailures andgooddata. Tests pass. Queue readiness is not GPUtiming qualification.

Results will appear under native-shader-paired512/<timestamp>; queue driver/provenance status under native-shader-performance/<timestamp>. No combined quantizer+Q3+SwiGLU mode exists yet; do not add estimated gains. Current-production comparison and longer-prompt/context qualification remain pending.
