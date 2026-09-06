"""
2_tm_to_mlir.py
===============
Compiles a Tsetlin Machine model into MLIR (Multi-Level Intermediate Representation).

Generates two complementary MLIR representations:
1. Standard Lowered MLIR (`generated/model.mlir`):
   - Uses core LLVM dialects: `func`, `arith`
   - Expresses literal inversion, clause AND-reduction trees, voting accumulation, and decision comparator in standard SSA form.
2. High-Level Domain MLIR (`generated/model_high_level.mlir`):
   - Uses a structured `tm` dialect (`tm.clause`, `tm.vote_accumulate`, `tm.threshold`)

Also includes an MLIR SSA software simulation engine to execute the generated MLIR code directly.
"""

import os
import json

class MLIREmitter:
    """
    Emits clean, syntactically valid MLIR for Tsetlin Machine inference.
    """
    def __init__(self, tm_model_path="./generated/tm_model.json"):
        with open(tm_model_path, "r") as f:
            self.model = json.load(f)
            
        self.num_inputs = self.model["num_inputs"]
        self.clauses = self.model["clauses"]
        self.benchmark_name = self.model["benchmark_name"]

    def emit_lowered_mlir(self):
        """
        Emits standard LLVM 'func' and 'arith' dialect MLIR.
        """
        fn_name = f"tsetlin_machine_{self.benchmark_name}"
        input_args = ", ".join([f"%x{i}: i1" for i in range(1, self.num_inputs + 1)])
        
        lines = []
        lines.append("// ==========================================================================")
        lines.append(f"// MLIR Representation for Tsetlin Machine ({self.benchmark_name.upper()} Benchmark)")
        lines.append("// Dialects: func, arith")
        lines.append("// Compiled from Canonical Tsetlin Machine Model")
        lines.append("// ==========================================================================")
        lines.append("module {")
        lines.append(f"  func.func @{fn_name}({input_args}) -> i1 {{")
        
        # 1. Constants & Literals (Inversion)
        lines.append("    // ------------------------------------------------------------------------")
        lines.append("    // Stage 0: Literal Generation (Primary Inputs & Inverters)")
        lines.append("    // ------------------------------------------------------------------------")
        lines.append("    %c1_i1 = arith.constant 1 : i1")
        for i in range(1, self.num_inputs + 1):
            lines.append(f"    %not_x{i} = arith.xori %x{i}, %c1_i1 : i1")

        # 2. Clause Conjunction Logic
        lines.append("")
        lines.append("    // ------------------------------------------------------------------------")
        lines.append("    // Stage 1: Clause Conjunction Trees (Bitwise AND Reductions)")
        lines.append("    // ------------------------------------------------------------------------")
        
        pos_clause_vars = []
        neg_clause_vars = []
        
        for c in self.clauses:
            cid = c["clause_id"]
            cname = c["clause_name"]
            lits = c["included_literals"]
            ssa_name = f"%{cname.lower()}"
            
            if len(lits) == 0:
                lines.append(f"    {ssa_name} = arith.constant 0 : i1  // Empty clause")
            elif len(lits) == 1:
                lines.append(f"    {ssa_name} = arith.andi %{lits[0]}, %c1_i1 : i1  // {c['formula']}")
            else:
                # Chain AND operations
                current_var = f"%{lits[0]}"
                for step, next_lit in enumerate(lits[1:]):
                    temp_var = ssa_name if step == len(lits) - 2 else f"%{cname.lower()}_step{step}"
                    lines.append(f"    {temp_var} = arith.andi {current_var}, %{next_lit} : i1")
                    current_var = temp_var
                    
            if c["polarity"] == +1:
                pos_clause_vars.append(ssa_name)
            else:
                neg_clause_vars.append(ssa_name)

        # 3. Voting Adder Tree
        lines.append("")
        lines.append("    // ------------------------------------------------------------------------")
        lines.append("    // Stage 2: Voting & Accumulation Tree")
        lines.append("    // ------------------------------------------------------------------------")
        
        # Zero-extend clause outputs to i32 for voting
        pos_ext_vars = []
        for v in pos_clause_vars:
            ext_v = f"{v}_ext"
            lines.append(f"    {ext_v} = arith.extui {v} : i1 to i32")
            pos_ext_vars.append(ext_v)

        neg_ext_vars = []
        for v in neg_clause_vars:
            ext_v = f"{v}_ext"
            lines.append(f"    {ext_v} = arith.extui {v} : i1 to i32")
            neg_ext_vars.append(ext_v)

        # Sum positive votes
        if len(pos_ext_vars) == 1:
            lines.append(f"    %pos_votes = arith.addi {pos_ext_vars[0]}, %c0_i32 : i32")
        else:
            cur_sum = pos_ext_vars[0]
            for step, next_v in enumerate(pos_ext_vars[1:]):
                sum_var = "%pos_votes" if step == len(pos_ext_vars) - 2 else f"%pos_sum_{step}"
                lines.append(f"    {sum_var} = arith.addi {cur_sum}, {next_v} : i32")
                cur_sum = sum_var

        # Sum negative votes
        if len(neg_ext_vars) == 1:
            lines.append(f"    %neg_votes = arith.addi {neg_ext_vars[0]}, %c0_i32 : i32")
        else:
            cur_sum = neg_ext_vars[0]
            for step, next_v in enumerate(neg_ext_vars[1:]):
                sum_var = "%neg_votes" if step == len(neg_ext_vars) - 2 else f"%neg_sum_{step}"
                lines.append(f"    {sum_var} = arith.addi {cur_sum}, {next_v} : i32")
                cur_sum = sum_var

        # 4. Threshold Subtractor & Comparator
        lines.append("")
        lines.append("    // ------------------------------------------------------------------------")
        lines.append("    // Stage 3: Decision Subtraction & Threshold Comparator")
        lines.append("    // ------------------------------------------------------------------------")
        lines.append("    %diff = arith.subi %pos_votes, %neg_votes : i32")
        lines.append("    %c0_i32 = arith.constant 0 : i32")
        lines.append("    %decision = arith.cmpi sge, %diff, %c0_i32 : i32")
        lines.append("")
        lines.append("    return %decision : i1")
        lines.append("  }")
        lines.append("}")
        
        return "\n".join(lines)

    def emit_high_level_mlir(self):
        """
        Emits domain-specific 'tm' dialect MLIR.
        """
        fn_name = f"tm_highlevel_{self.benchmark_name}"
        input_args = ", ".join([f"%x{i}: i1" for i in range(1, self.num_inputs + 1)])
        
        lines = []
        lines.append("// ==========================================================================")
        lines.append(f"// High-Level 'tm' Dialect MLIR Representation ({self.benchmark_name.upper()})")
        lines.append("// ==========================================================================")
        lines.append("module {")
        lines.append(f"  func.func @{fn_name}({input_args}) -> i1 {{")
        lines.append("    %literals = tm.literal_extract(%x1, %x2) : (i1, i1) -> !tm.literals<4>")
        
        pos_names = []
        neg_names = []
        for c in self.clauses:
            mask_str = str(c["include_mask"])
            cname = f"%{c['clause_name'].lower()}"
            pol_str = "pos" if c["polarity"] == 1 else "neg"
            lines.append(f"    {cname} = tm.clause(%literals) {{include_mask = {mask_str}, polarity = \"{pol_str}\"}} : (!tm.literals<4>) -> i1")
            if c["polarity"] == +1:
                pos_names.append(cname)
            else:
                neg_names.append(cname)
                
        pos_args = ", ".join(pos_names)
        neg_args = ", ".join(neg_names)
        lines.append(f"    %pos_votes = tm.vote_accumulate({pos_args}) : i32")
        lines.append(f"    %neg_votes = tm.vote_accumulate({neg_args}) : i32")
        lines.append("    %decision = tm.threshold(%pos_votes, %neg_votes) : (i32, i32) -> i1")
        lines.append("    return %decision : i1")
        lines.append("  }")
        lines.append("}")
        return "\n".join(lines)

    def simulate_mlir(self, X):
        """
        Executes an exact software simulation of the lowered MLIR SSA instruction stream.
        """
        env = {}
        # Arguments
        for i, val in enumerate(X, 1):
            env[f"%x{i}"] = int(val)
            
        # Constants
        env["%c1_i1"] = 1
        env["%c0_i32"] = 0
        
        # Stage 0: Inversions
        for i in range(1, self.num_inputs + 1):
            env[f"%not_x{i}"] = 1 - env[f"%x{i}"]
            
        # Stage 1: Clause Conjunctions
        pos_vars = []
        neg_vars = []
        for c in self.clauses:
            cname = c["clause_name"]
            lits = c["included_literals"]
            ssa_name = f"%{cname.lower()}"
            
            val = 1
            for lit in lits:
                val = val & env[f"%{lit}"]
            env[ssa_name] = val
            
            if c["polarity"] == +1:
                pos_vars.append(ssa_name)
            else:
                neg_vars.append(ssa_name)
                
        # Stage 2: Voting Extension & Sum
        pos_sum = sum(env[v] for v in pos_vars)
        neg_sum = sum(env[v] for v in neg_vars)
        env["%pos_votes"] = pos_sum
        env["%neg_votes"] = neg_sum
        
        # Stage 3: Subtraction & Decision
        diff = pos_sum - neg_sum
        decision = 1 if diff >= 0 else 0
        env["%diff"] = diff
        env["%decision"] = decision
        
        return env

def compile_and_save_mlir(tm_model_path="./generated/tm_model.json", output_dir="./generated"):
    os.makedirs(output_dir, exist_ok=True)
    emitter = MLIREmitter(tm_model_path)
    
    # Lowered MLIR
    lowered_code = emitter.emit_lowered_mlir()
    lowered_path = os.path.join(output_dir, "model.mlir")
    with open(lowered_path, "w") as f:
        f.write(lowered_code)
        
    # High Level MLIR
    hl_code = emitter.emit_high_level_mlir()
    hl_path = os.path.join(output_dir, "model_high_level.mlir")
    with open(hl_path, "w") as f:
        f.write(hl_code)

    print(f"[2_tm_to_mlir] Successfully compiled Tsetlin Machine to MLIR:")
    print(f"               - Lowered Standard MLIR (arith/func) : {lowered_path}")
    print(f"               - High-Level Domain MLIR (tm)        : {hl_path}")
    
    # Test MLIR simulation across truth table
    print("               Validating MLIR Software Execution against Truth Table:")
    test_inputs = [(0, 0), (0, 1), (1, 0), (1, 1)]
    for inp in test_inputs:
        sim_res = emitter.simulate_mlir(inp)
        expected = inp[0] ^ inp[1]
        passed = (sim_res["%decision"] == expected)
        status = "PASSED" if passed else "FAILED"
        print(f"               Input {inp} -> Decision: {sim_res['%decision']} (Expected: {expected}) [{status}]")
        
    return emitter

if __name__ == "__main__":
    compile_and_save_mlir()
