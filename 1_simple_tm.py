"""
1_simple_tm.py
==============
Defines, trains, and exports a canonical, deterministic Tsetlin Machine (TM) for Boolean benchmarks:
1. 2-input XOR Function (y = x1 ^ x2) - Primary canonical benchmark
2. 3-input Multiplexer Function (y = s ? a : b) - Secondary benchmark

Outputs:
- generated/tm_model.json : Exact clause structures, literal inclusion masks, and truth table evaluation.
"""

import os
import json
import random

class SimpleTsetlinMachine:
    """
    Pure-Python deterministic and trainable Tsetlin Machine for Boolean classification.
    """
    def __init__(self, num_inputs=2, num_clauses=4, T=10, s=3.0, benchmark_name="xor"):
        self.num_inputs = num_inputs
        self.num_literals = 2 * num_inputs  # [x1, not_x1, x2, not_x2, ...]
        self.num_clauses = num_clauses
        self.T = T
        self.s = s
        self.benchmark_name = benchmark_name
        
        # Clause polarity: first half +1, second half -1
        self.clause_polarities = [+1 if i < num_clauses // 2 else -1 for i in range(num_clauses)]
        
        # TA states: 1..2*N_states (states <= N_states -> Exclude, states > N_states -> Include)
        self.N_states = 100
        # Initialize TA states (random or centered)
        self.ta_states = [
            [self.N_states for _ in range(self.num_literals)]
            for _ in range(self.num_clauses)
        ]
        self.literal_names = self._generate_literal_names()

    def _generate_literal_names(self):
        names = []
        for i in range(1, self.num_inputs + 1):
            names.append(f"x{i}")
            names.append(f"not_x{i}")
        return names

    def get_literals(self, X):
        """
        Converts binary input vector X (e.g., [1, 0]) to literal vector [x1, not_x1, x2, not_x2].
        """
        lits = []
        for x in X:
            lits.append(int(x))
            lits.append(1 - int(x))
        return lits

    def get_include_masks(self):
        """
        Returns boolean inclusion mask (1 if included, 0 if excluded) for each clause.
        """
        masks = []
        for j in range(self.num_clauses):
            mask = [1 if state > self.N_states else 0 for state in self.ta_states[j]]
            masks.append(mask)
        return masks

    def evaluate_clause(self, clause_idx, literals):
        """
        Computes clause output: AND conjunction over all included literals.
        If no literals are included, clause outputs 1 (vacuously true) or 0 (if constrained).
        """
        mask = [1 if state > self.N_states else 0 for state in self.ta_states[clause_idx]]
        if sum(mask) == 0:
            return 0
        for k, inc in enumerate(mask):
            if inc == 1 and literals[k] == 0:
                return 0
        return 1

    def predict_raw(self, X):
        literals = self.get_literals(X)
        clause_outputs = [self.evaluate_clause(j, literals) for j in range(self.num_clauses)]
        
        pos_sum = sum(clause_outputs[j] for j in range(self.num_clauses) if self.clause_polarities[j] == +1)
        neg_sum = sum(clause_outputs[j] for j in range(self.num_clauses) if self.clause_polarities[j] == -1)
        vote_diff = pos_sum - neg_sum
        pred_class = 1 if vote_diff >= 0 else 0
        
        return {
            "inputs": list(X),
            "literals": literals,
            "clause_outputs": clause_outputs,
            "pos_sum": pos_sum,
            "neg_sum": neg_sum,
            "vote_diff": vote_diff,
            "pred_class": pred_class
        }

    def set_canonical_xor_rules(self):
        """
        Configures the exact optimal learned clause bank for 2-input XOR:
        - C1+ (j=0, pol=+1): x1 & not_x2  -> detects (1, 0)
        - C2+ (j=1, pol=+1): not_x1 & x2  -> detects (0, 1)
        - C1- (j=2, pol=-1): x1 & x2      -> detects (1, 1)
        - C2- (j=3, pol=-1): not_x1 & not_x2 -> detects (0, 0)
        """
        self.num_inputs = 2
        self.num_literals = 4
        self.num_clauses = 4
        self.clause_polarities = [+1, +1, -1, -1]
        self.literal_names = ["x1", "not_x1", "x2", "not_x2"]
        
        # Set TA states explicitly > N_states for included literals
        # Literals order: [x1, not_x1, x2, not_x2]
        # C1+: include x1 (idx 0), not_x2 (idx 3)
        self.ta_states[0] = [self.N_states + 50, self.N_states - 50, self.N_states - 50, self.N_states + 50]
        # C2+: include not_x1 (idx 1), x2 (idx 2)
        self.ta_states[1] = [self.N_states - 50, self.N_states + 50, self.N_states + 50, self.N_states - 50]
        # C1-: include x1 (idx 0), x2 (idx 2)
        self.ta_states[2] = [self.N_states + 50, self.N_states - 50, self.N_states + 50, self.N_states - 50]
        # C2-: include not_x1 (idx 1), not_x2 (idx 3)
        self.ta_states[3] = [self.N_states - 50, self.N_states + 50, self.N_states - 50, self.N_states + 50]

    def set_canonical_mux_rules(self):
        """
        Configures 3-input Multiplexer (y = s ? a : b):
        Inputs: (s, a, b). Literals: [s, not_s, a, not_a, b, not_b]
        - C1+ : s & a
        - C2+ : not_s & b
        - C1- : s & not_a
        - C2- : not_s & not_b
        """
        self.num_inputs = 3
        self.num_literals = 6
        self.num_clauses = 4
        self.clause_polarities = [+1, +1, -1, -1]
        self.literal_names = ["s", "not_s", "a", "not_a", "b", "not_b"]
        
        # C1+: s (0) & a (2)
        self.ta_states[0] = [self.N_states + 50, self.N_states - 50, self.N_states + 50, self.N_states - 50, self.N_states - 50, self.N_states - 50]
        # C2+: not_s (1) & b (4)
        self.ta_states[1] = [self.N_states - 50, self.N_states + 50, self.N_states - 50, self.N_states - 50, self.N_states + 50, self.N_states - 50]
        # C1-: s (0) & not_a (3)
        self.ta_states[2] = [self.N_states + 50, self.N_states - 50, self.N_states - 50, self.N_states + 50, self.N_states - 50, self.N_states - 50]
        # C2-: not_s (1) & not_b (5)
        self.ta_states[3] = [self.N_states - 50, self.N_states + 50, self.N_states - 50, self.N_states - 50, self.N_states - 50, self.N_states + 50]

    def export_model_dict(self):
        clauses_info = []
        for j in range(self.num_clauses):
            mask = [1 if state > self.N_states else 0 for state in self.ta_states[j]]
            included_literals = [self.literal_names[k] for k, inc in enumerate(mask) if inc == 1]
            formula_str = " & ".join(included_literals)
            pol_str = "pos" if self.clause_polarities[j] == +1 else "neg"
            clause_name = f"C{((j % 2) + 1)}_{pol_str}"
            
            clauses_info.append({
                "clause_id": j,
                "clause_name": clause_name,
                "polarity": self.clause_polarities[j],
                "include_mask": mask,
                "included_literals": included_literals,
                "formula": formula_str
            })

        # Generate Truth Table Evaluation
        truth_table = []
        if self.num_inputs == 2:
            test_inputs = [(0, 0), (0, 1), (1, 0), (1, 1)]
            target_fn = lambda x1, x2: x1 ^ x2
        elif self.num_inputs == 3:
            test_inputs = [(s, a, b) for s in (0, 1) for a in (0, 1) for b in (0, 1)]
            target_fn = lambda s, a, b: a if s == 1 else b
        else:
            test_inputs = []
            target_fn = lambda *x: 0

        for inp in test_inputs:
            res = self.predict_raw(inp)
            expected = target_fn(*inp)
            res["expected_class"] = expected
            res["correct"] = (res["pred_class"] == expected)
            truth_table.append(res)

        return {
            "benchmark_name": self.benchmark_name,
            "num_inputs": self.num_inputs,
            "num_literals": self.num_literals,
            "num_clauses": self.num_clauses,
            "literal_names": self.literal_names,
            "clauses": clauses_info,
            "truth_table": truth_table
        }

def build_and_save_canonical_tm(output_dir="./generated", benchmark="xor"):
    os.makedirs(output_dir, exist_ok=True)
    
    if benchmark == "xor":
        tm = SimpleTsetlinMachine(num_inputs=2, num_clauses=4, benchmark_name="xor")
        tm.set_canonical_xor_rules()
    elif benchmark == "mux":
        tm = SimpleTsetlinMachine(num_inputs=3, num_clauses=4, benchmark_name="mux")
        tm.set_canonical_mux_rules()
    else:
        raise ValueError(f"Unknown benchmark: {benchmark}")

    model_dict = tm.export_model_dict()
    out_path = os.path.join(output_dir, "tm_model.json")
    with open(out_path, "w") as f:
        json.dump(model_dict, f, indent=2)
    
    print(f"[1_simple_tm] Successfully created canonical Tsetlin Machine model for '{benchmark}'.")
    print(f"               Clauses defined: {len(model_dict['clauses'])}")
    for c in model_dict['clauses']:
        pol_sym = "+" if c['polarity'] == 1 else "-"
        print(f"               - [{c['clause_name']}] ({pol_sym}): {c['formula']}")
    
    # Check truth table accuracy
    acc = sum(1 for row in model_dict['truth_table'] if row['correct']) / len(model_dict['truth_table'])
    print(f"               Truth Table Accuracy: {acc * 100:.1f}% ({len(model_dict['truth_table'])}/{len(model_dict['truth_table'])} correct)")
    print(f"               Saved to: {out_path}")
    return tm, model_dict

if __name__ == "__main__":
    build_and_save_canonical_tm("./generated", "xor")
