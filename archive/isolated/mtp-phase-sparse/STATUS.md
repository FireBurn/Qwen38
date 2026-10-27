# Sparse phase profiler

Separate copy of denseprofile host/shader. Deterministic32bit hash(record+tbase) selects1/8 in expectation. Separate deviceprofile slots zeroed beforeeachdispatch; CPU exports onlywritten rows. No live counter/tape changes.16sampledWGs include first/last. Source and SPIR-V build+validation complete.

Initial16WG parent/off/on all native-bit-exact across64graphs,4inputpatterns,0/1/2bias outputs. Profile shader96VGPR/56SGPRspills/16KiBLDS/0scratch. An incorrect harness assertion expected<150rows; actual short9recordgraph hashes select3records, giving186/558rows. GPUchild had exited0 and numerical/resourcechecks passed. Revalidated terminal artifacts, confirmed hashmembership and positive ordered clocks; removed arbitrary countbound. No GPUrerun or crash for this assertion.

Full192WG Roman64requested/66emitted: parent/off/on each matches114full reference logit/hidden records, all tokens and28/38acceptance; last12graphs allmega. Export1812rows versus14220dense acrosssame12graphs (7.85xless). All selected opcode/workgrids/pushconstants agree with dense reference atsamegraph/recordindex. Parent35.963t/s,off36.058,on34.511 in one under-load unpaired batch. Active profiling slowdown about4.29%, versus prior dense13.25%; not precise calibrated overhead due changedload/clock and CPUdump/wait behavior.

Raw sampled target barrier fractions8.4-10.0%are exploratory. Hashseeds repeat acrossparity and may miss rare expensive operators (e.g.single outputhead); sampling composition differs, so do not interpret the reduction fromdense13%as removed barrier overhead or extrapolate naivefractions to fullruntime. Source-derived terminal counter claims motivated a separate uninstrumented candidate; that candidate didnotestablish a modelgain. Leave profiler unpromoted for precise attribution. A future useful sampler should stratify expensive/rareoperators, rotate seeds, and report population/samplecoverage, then bound observer overhead.

Original dense artifacts preserved. Quietwaiter resumed; no production changes.
