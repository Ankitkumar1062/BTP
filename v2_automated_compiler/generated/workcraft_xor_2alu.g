# Workcraft CPOG Model Specification
# Benchmark: XOR Tsetlin Machine
# Scenario Variables: 
.model cpog_tsetlin_machine

.inputs 

# Vertices and Activation Conditions phi(v)
.vertex in_x1 [label="Port x1"] [cond="1"]
.vertex in_not_x1 [label="Port not_x1"] [cond="1"]
.vertex in_x2 [label="Port x2"] [cond="1"]
.vertex in_not_x2 [label="Port not_x2"] [cond="1"]
.vertex mux1_core0 [label="MUX1 C0"] [cond="1"]
.vertex mux2_core0 [label="MUX2 C0"] [cond="1"]
.vertex and_core0 [label="AND C0"] [cond="1"]
.vertex acc_core0 [label="ACC C0"] [cond="1"]
.vertex mux1_core1 [label="MUX1 C1"] [cond="1"]
.vertex mux2_core1 [label="MUX2 C1"] [cond="1"]
.vertex and_core1 [label="AND C1"] [cond="1"]
.vertex acc_core1 [label="ACC C1"] [cond="1"]
.vertex decision_cmp [label="Threshold Comparator"] [cond="1"]

# Directed Arcs and Routing Conditions rho(e)
.arc mux1_core0 -> and_core0 [cond="1"] [sop="1"]
.arc mux2_core0 -> and_core0 [cond="1"] [sop="1"]
.arc and_core0 -> acc_core0 [cond="1"] [sop="1"]
.arc mux1_core1 -> and_core1 [cond="1"] [sop="1"]
.arc mux2_core1 -> and_core1 [cond="1"] [sop="1"]
.arc and_core1 -> acc_core1 [cond="1"] [sop="1"]
.arc in_x1 -> mux1_core0 [cond="1"] [sop="1"]
.arc in_not_x2 -> mux2_core0 [cond="1"] [sop="1"]
.arc in_not_x1 -> mux1_core1 [cond="1"] [sop="1"]
.arc in_x2 -> mux2_core1 [cond="1"] [sop="1"]
.arc acc_core0 -> decision_cmp [cond="1"] [sop="1"]
.arc acc_core1 -> decision_cmp [cond="1"] [sop="1"]

# Operational Scenarios (Opcodes)
# Scenario  -> C1_pos, C2_pos (x1 & not_x2, not_x1 & x2)
.scenario step_0 static=1
.end