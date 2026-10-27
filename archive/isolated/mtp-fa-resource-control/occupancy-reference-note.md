# Occupancy references

AMD GPUOpen explains that more resident waves help only when useful latency can be hidden, and can hurt cache behavior or fail to help a bandwidth-saturated shader: https://gpuopen.com/learn/occupancy-explained/ . It also distinguishes theoretical from measuredoccupancy.

R9700actualresourcecoefficients come fromourfrozen-driver RADV_DEBUG=info query, not from anotherGPU's example. Mesa allocationcounts usewave64-equivalentVGPR units,12-registergranularity and wave-size conversion; maxwaves code inspected in aco_live_var_analysis.cpp and radv_shader.c. Both CU/WGP residencybounds considered, lowerbound used. This is a source-derived capacity estimate, not directlymeasuredoccupancy. Allcustomshader variantsfirst<=16physicalWG;256launchesonlyafter72VGPR/2KiB/0scratchand320-capacitygate. No furthergridincreasequalified.
