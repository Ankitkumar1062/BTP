# Workcraft CPOG Model Specification
# Benchmark: XOR Tsetlin Machine
# Scenario Variables: s1, s0
.model cpog_tsetlin_machine

.inputs s1 s0

# Vertices and Activation Conditions phi(v)
.vertex in_x1 [label="Input Port x1"] [cond="1"]
.vertex in_not_x1 [label="Input Port ~x1"] [cond="1"]
.vertex in_x2 [label="Input Port x2"] [cond="1"]
.vertex in_not_x2 [label="Input Port ~x2"] [cond="1"]
.vertex lit_mux1 [label="Literal MUX 1"] [cond="1"]
.vertex lit_mux2 [label="Literal MUX 2"] [cond="1"]
.vertex and_core [label="Shared 2-input AND Core"] [cond="1"]
.vertex acc_core [label="Reconfigurable Accumulator (+/-)"] [cond="1"]
.vertex decision_cmp [label="Threshold Comparator (>= 0)"] [cond="1"]

# Directed Arcs and Routing Conditions rho(e)
.arc in_x1 -> lit_mux1 [cond="~s0"] [sop="~s1.~s0 + s1.~s0"]
.arc in_not_x1 -> lit_mux1 [cond="s0"] [sop="~s1.s0 + s1.s0"]
.arc in_x2 -> lit_mux2 [cond="s1 ^ s0"] [sop="~s1.s0 + s1.~s0"]
.arc in_not_x2 -> lit_mux2 [cond="~(s1 ^ s0)"] [sop="~s1.~s0 + s1.s0"]
.arc lit_mux1 -> and_core [cond="1"] [sop="1"]
.arc lit_mux2 -> and_core [cond="1"] [sop="1"]
.arc and_core -> acc_core [cond="1"] [sop="1"]
.arc acc_core -> decision_cmp [cond="1"] [sop="1"]

# Operational Scenarios (Opcodes)
# Scenario 00 -> C1_pos (x1 & ~x2)
.scenario C1_pos s1=0 s0=0
# Scenario 01 -> C2_pos (~x1 & x2)
.scenario C2_pos s1=0 s0=1
# Scenario 10 -> C1_neg (x1 & x2)
.scenario C1_neg s1=1 s0=0
# Scenario 11 -> C2_neg (~x1 & ~x2)
.scenario C2_neg s1=1 s0=1
.end