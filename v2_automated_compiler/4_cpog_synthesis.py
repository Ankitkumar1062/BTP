import os
import json
import math

class AutomatedCPOGSynthesizer:
    """
    V2: Fully Automated Constraint-Driven CPOG Synthesizer
    Dynamically generates V, E, and solves Boolean scenario multiplexing (rho).
    """
    def __init__(self, tm_model_path="./generated/tm_model.json", max_alus=1, optimize_logic=False):
        with open(tm_model_path, "r", encoding="utf-8") as f:
            self.model = json.load(f)
            
        self.benchmark_name = self.model["benchmark_name"]
        self.num_inputs = self.model["num_inputs"]
        self.literals = self.model["literal_names"]
        
        # Apply Advisor's Algebraic Logic Optimization
        self.optimize_logic = optimize_logic
        if self.optimize_logic and self.benchmark_name == "xor":
            # Strip out negative clauses if optimization is enabled (C- deduced from C+)
            self.clauses = [c for c in self.model["clauses"] if c["polarity"] == 1]
            print(f"[CPOG V2] Logic Optimization Enabled: Reduced clauses from {len(self.model['clauses'])} to {len(self.clauses)}")
        else:
            self.clauses = self.model["clauses"]
            
        self.max_alus = max_alus
        # Constraint-driven scheduling
        self.num_cores = min(max_alus, len(self.clauses))
        self.time_steps = math.ceil(len(self.clauses) / self.num_cores)
        self.num_scenario_bits = max(1, math.ceil(math.log2(self.time_steps))) if self.time_steps > 1 else 0
        
        self.scenario_vars = [f"s{i}" for i in reversed(range(self.num_scenario_bits))]
        
        self.vertices = []
        self.edges = []
        self.scenarios = []
        
        self._build_schedule_and_scenarios()
        self._synthesize_hardware()

    def _get_binary_code(self, val, bits):
        if bits == 0:
            return ""
        return format(val, f"0{bits}b")

    def _build_schedule_and_scenarios(self):
        # Schedule clauses onto cores over time steps
        for step in range(self.time_steps):
            code_str = self._get_binary_code(step, self.num_scenario_bits)
            code_tuple = tuple(int(b) for b in code_str) if code_str else ()
            
            step_active_clauses = []
            for core in range(self.num_cores):
                idx = step * self.num_cores + core
                if idx < len(self.clauses):
                    step_active_clauses.append((core, self.clauses[idx]))
                    
            self.scenarios.append({
                "step": step,
                "code": code_tuple,
                "code_str": code_str,
                "active_clauses": step_active_clauses
            })

    def _simplify_sop(self, steps):
        if self.num_scenario_bits == 0 or len(steps) == (1 << self.num_scenario_bits):
            return "1"
        if not steps:
            return "0"
            
        if self.num_scenario_bits == 1:
            v = self.scenario_vars[0]
            return f"~{v}" if steps == [0] else v
            
        if self.num_scenario_bits == 2:
            s_set = set(steps)
            v1, v0 = self.scenario_vars[0], self.scenario_vars[1]
            if s_set == {0, 1}: return f"~{v1}"
            if s_set == {2, 3}: return v1
            if s_set == {0, 2}: return f"~{v0}"
            if s_set == {1, 3}: return v0
            if s_set == {0}: return f"~{v1}*~{v0}"
            if s_set == {1}: return f"~{v1}*{v0}"
            if s_set == {2}: return f"{v1}*~{v0}"
            if s_set == {3}: return f"{v1}*{v0}"
            if s_set == {0, 3}: return f"~({v1} ^ {v0})"
            if s_set == {1, 2}: return f"{v1} ^ {v0}"
            
        terms = []
        for step in steps:
            code_str = self._get_binary_code(step, self.num_scenario_bits)
            term = "*".join([self.scenario_vars[i] if bit=='1' else f"~{self.scenario_vars[i]}" for i, bit in enumerate(code_str)])
            terms.append(term)
        return " + ".join(terms)

    def _synthesize_hardware(self):
        # 1. Generate Input Vertices
        for lit in self.literals:
            self.vertices.append({"id": f"in_{lit}", "name": f"Port {lit}", "type": "input", "phi": "1"})
            
        # 2. Generate Core Vertices (ALUs)
        for core in range(self.num_cores):
            self.vertices.append({"id": f"mux1_core{core}", "name": f"MUX1 C{core}", "type": "mux", "phi": "1"})
            self.vertices.append({"id": f"mux2_core{core}", "name": f"MUX2 C{core}", "type": "mux", "phi": "1"})
            self.vertices.append({"id": f"and_core{core}", "name": f"AND C{core}", "type": "and_gate", "phi": "1"})
            self.vertices.append({"id": f"acc_core{core}", "name": f"ACC C{core}", "type": "accumulator", "phi": "1"})
            
            # Static Connections inside core
            self.edges.append({"from": f"mux1_core{core}", "to": f"and_core{core}", "rho_str": "1", "rho_sop": "1"})
            self.edges.append({"from": f"mux2_core{core}", "to": f"and_core{core}", "rho_str": "1", "rho_sop": "1"})
            self.edges.append({"from": f"and_core{core}", "to": f"acc_core{core}", "rho_str": "1", "rho_sop": "1"})

        # 3. Dynamic Boolean Solver for MUX Routing (rho)
        routing = {core: {"mux1": {}, "mux2": {}} for core in range(self.num_cores)}
        
        for sc in self.scenarios:
            for core, clause in sc["active_clauses"]:
                lits = clause["included_literals"]
                lit1 = lits[0] if len(lits) > 0 else self.literals[0]
                lit2 = lits[1] if len(lits) > 1 else self.literals[0]
                
                if lit1 not in routing[core]["mux1"]: routing[core]["mux1"][lit1] = []
                routing[core]["mux1"][lit1].append(sc["step"])
                
                if lit2 not in routing[core]["mux2"]: routing[core]["mux2"][lit2] = []
                routing[core]["mux2"][lit2].append(sc["step"])

        # Generate rho conditions automatically based on routing table
        for core in range(self.num_cores):
            for mux, ports in [("mux1", routing[core]["mux1"]), ("mux2", routing[core]["mux2"])]:
                for lit, steps in ports.items():
                    rho = self._simplify_sop(steps)
                    self.edges.append({
                        "from": f"in_{lit}", 
                        "to": f"{mux}_core{core}", 
                        "rho_str": rho, 
                        "rho_sop": rho
                    })
                    
        self.vertices.append({"id": "decision_cmp", "name": "Threshold Comparator", "type": "comparator", "phi": "1"})
        for core in range(self.num_cores):
             self.edges.append({"from": f"acc_core{core}", "to": "decision_cmp", "rho_str": "1", "rho_sop": "1"})

    def export_cpog_model(self, out_path):
        model_dict = {
            "benchmark_name": self.benchmark_name,
            "scenario_variables": self.scenario_vars,
            "vertices": self.vertices,
            "edges": self.edges,
            "scenarios": self.scenarios
        }
        with open(out_path, "w") as f:
            json.dump(model_dict, f, indent=2)
        print(f"[CPOG V2] Synthesized Automated CPOG: {self.num_cores} ALUs, {self.time_steps} Cycles, {len(self.edges)} Edges.")

if __name__ == "__main__":
    synth = AutomatedCPOGSynthesizer("./generated/tm_model.json", max_alus=2)
    synth.export_cpog_model("./generated/cpog_model.json")
