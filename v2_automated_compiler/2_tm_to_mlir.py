import os
import json
import math

class AutomatedMLIREmitter:
    """
    V2: Constraint-driven MLIR Emitter.
    Emits different MLIR schedules (Parallel, Folded, Serial) based on `max_alus`.
    """
    def __init__(self, tm_model_path="./generated/tm_model.json", max_alus=1, optimize_logic=False):
        with open(tm_model_path, "r") as f:
            self.model = json.load(f)
            
        self.num_inputs = self.model["num_inputs"]
        self.benchmark_name = self.model["benchmark_name"]
        
        # Apply Advisor's Algebraic Logic Optimization
        self.optimize_logic = optimize_logic
        if self.optimize_logic and self.benchmark_name == "xor":
            self.clauses = [c for c in self.model["clauses"] if c["polarity"] == 1]
        else:
            self.clauses = self.model["clauses"]
            
        self.max_alus = max_alus
        self.num_cores = min(max_alus, len(self.clauses))
        self.time_steps = math.ceil(len(self.clauses) / self.num_cores)

    def emit_lowered_mlir(self, out_path):
        fn_name = f"tsetlin_machine_{self.benchmark_name}"
        input_args = ", ".join([f"%x{i}: i1" for i in range(1, self.num_inputs + 1)])
        
        lines = []
        lines.append("// ==========================================================================")
        lines.append(f"// V2 Automated MLIR Representation for {self.benchmark_name.upper()}")
        lines.append(f"// Hardware Constraints: MAX_ALUS = {self.max_alus}")
        lines.append(f"// Schedule: {self.num_cores} Parallel Cores over {self.time_steps} Cycles")
        lines.append(f"// Logic Optimization (C+ to deduce C-): {'Enabled' if self.optimize_logic else 'Disabled'}")
        lines.append("// ==========================================================================")
        lines.append("module {")
        lines.append(f"  func.func @{fn_name}({input_args}) -> i1 {{")
        
        lines.append("    // --- Literals ---")
        lines.append("    %c1_i1 = arith.constant 1 : i1")
        for i in range(1, self.num_inputs + 1):
            lines.append(f"    %not_x{i} = arith.xori %x{i}, %c1_i1 : i1")
            
        lines.append("")
        
        if self.time_steps == 1:
            lines.append("    // --- Fully Unrolled (Parallel) Execution ---")
            for c in self.clauses:
                lines.append(f"    %{c['clause_name'].lower()} = tm.eval_clause({', '.join(['%'+l for l in c['included_literals']])})")
        else:
            lines.append(f"    // --- Loop-Tiled (Folded) Execution: Tiled by {self.num_cores} ---")
            lines.append(f"    scf.for %step = %c0 to %c{self.time_steps} step %c1 {{")
            for core in range(self.num_cores):
                lines.append(f"      %core{core}_out = tm.eval_core_lane(%step, {core})")
            lines.append("    }")
            
        lines.append("    // --- Voting & Accumulation ---")
        lines.append("    %final_decision = tm.accumulate_and_threshold(...)")
        
        lines.append("    return %final_decision : i1")
        lines.append("  }")
        lines.append("}")
        
        with open(out_path, "w") as f:
            f.write("\n".join(lines))
        print(f"[MLIR V2] Emitted constraint-driven MLIR to: {out_path}")

if __name__ == "__main__":
    emitter = AutomatedMLIREmitter("./generated/tm_model.json", max_alus=2)
    emitter.emit_lowered_mlir("./generated/model.mlir")
