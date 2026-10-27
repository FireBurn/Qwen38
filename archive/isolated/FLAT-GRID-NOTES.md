# Avoid general virtual-grid indexing in matvecs

Last saved full graph:497matvec calls,2076160 virtual tasks after row remapping; every grid has y=z=1. For a valid queued task v<total=x, original coordinates(v%x,(v/x)%y,v/(x*y)) are exactly(v,0,0). New guarded path affects only six LS64 matvec wrappers. Other shapes retain the old mapping. BF16 pairing may reduce v modulo its half-grid first; v remains valid, so both address mappings agree. Source builder checks queue bounds and min(g+chunk,total) before replacing the mapping. No shape-specific host ABI or descriptor changes.

Plain guard passes9/65-frame tests,96VGPR/24SGPRspills/16KB/code241448, but shortABBA is-0.669%. The local Mesa radv_shader.c enables expensive_alu_ok=true with select-folding limit8; nir_opt_peephole_select explicitly permitsudiv in that mode. It also honorsDontFlatten by setting limit0. This is a source-level reason to test branch retention, not proof of what the installed driver executed.

An explicit[[dont_flatten]] version passes9/65frames, same allocation,241532bytes code. All six DontFlatten selection merges survive SPIR-V optimization (flat-grid-selection-audit.json). Driver ISA capture has not been done; no ISA-cost attribution is established. Paired timing pending. Keep current BF16-pair reference until a measured gain exists.
