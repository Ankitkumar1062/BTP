"""
4_cpog_synthesis.py
===================
Synthesizes the formal Conditional Partial Order Graph (CPOG) H = (V, E, φ, ρ, S) for Tsetlin Machine execution.

Following Mokhov & Yakovlev (IEEE TC 2010), CPOG unifies multiple operational scenarios into a single
shared hardware datapath where:
- V: Shared hardware functional units (Literal Selectors, AND-Core, Accumulator, Comparator)
- E: Directed interconnect and routing channels
- S = (s1, s0): Boolean control scenario variables (clause selection opcodes)
- φ(v): Vertex activation conditions (drive clock-gating / enable logic)
- ρ(e): Arc routing conditions (drive multiplexer selection logic)

Outputs:
1. `generated/cpog_graph.dot` : Unified CPOG DOT representation with Boolean condition labels.
2. `generated/cpog_graph.svg` : Vector diagram of the synthesized CPOG datapath.
3. `generated/projections/`   : Individual projected graphs H|00, H|01, H|10, H|11.
4. `generated/cpog_model.json`: Mathematical CPOG tuple and Boolean equations for formal verification.
"""

import os
import json
import shutil
import subprocess

class CPOGSynthesizer:
    """
    Formal CPOG Synthesis and Projection Engine for Tsetlin Machines.
    """
    def __init__(self, tm_model_path="./generated/tm_model.json"):
        with open(tm_model_path, "r", encoding="utf-8") as f:
            self.model = json.load(f)
            
        self.benchmark_name = self.model["benchmark_name"]
        self.num_inputs = self.model["num_inputs"]
        self.clauses = self.model["clauses"]
        
        # Scenario definitions: 4 clauses mapped to 2 control bits S = (s1, s0)
        self.scenario_vars = ["s1", "s0"]
        self.scenarios = [
            {"code": (0, 0), "code_str": "00", "clause_name": "C1_pos", "formula": "x1 & ~x2", "polarity": +1},
            {"code": (0, 1), "code_str": "01", "clause_name": "C2_pos", "formula": "~x1 & x2", "polarity": +1},
            {"code": (1, 0), "code_str": "10", "clause_name": "C1_neg", "formula": "x1 & x2", "polarity": -1},
            {"code": (1, 1), "code_str": "11", "clause_name": "C2_neg", "formula": "~x1 & ~x2", "polarity": -1},
        ]
        
        self.vertices = []
        self.edges = []
        self._synthesize_cpog()

    def _synthesize_cpog(self):
        # 1. Vertices (Shared Hardware Units)
        # All core units have phi(v) = 1 (100% hardware reuse across all scenarios)
        self.vertices = [
            {"id": "in_x1", "name": "Input Port x1", "type": "input", "phi": "1", "phi_eval": lambda s1, s0: 1},
            {"id": "in_not_x1", "name": "Input Port ~x1", "type": "input", "phi": "1", "phi_eval": lambda s1, s0: 1},
            {"id": "in_x2", "name": "Input Port x2", "type": "input", "phi": "1", "phi_eval": lambda s1, s0: 1},
            {"id": "in_not_x2", "name": "Input Port ~x2", "type": "input", "phi": "1", "phi_eval": lambda s1, s0: 1},
            {"id": "lit_mux1", "name": "Literal MUX 1", "type": "mux", "phi": "1", "phi_eval": lambda s1, s0: 1},
            {"id": "lit_mux2", "name": "Literal MUX 2", "type": "mux", "phi": "1", "phi_eval": lambda s1, s0: 1},
            {"id": "and_core", "name": "Shared 2-input AND Core", "type": "and_gate", "phi": "1", "phi_eval": lambda s1, s0: 1},
            {"id": "acc_core", "name": "Reconfigurable Accumulator (+/-)", "type": "accumulator", "phi": "1", "phi_eval": lambda s1, s0: 1},
            {"id": "decision_cmp", "name": "Threshold Comparator (>= 0)", "type": "comparator", "phi": "1", "phi_eval": lambda s1, s0: 1},
        ]

        # 2. Synthesized Edge Routing Conditions (rho)
        # Derived from truth table over scenario codes (s1, s0):
        # MUX 1: selects x1 when s0=0, ~x1 when s0=1 -> rho(x1->Mux1) = ~s0, rho(~x1->Mux1) = s0
        # MUX 2: selects ~x2 for 00 and 11 (s1 == s0), x2 for 01 and 10 (s1 != s0)
        # -> rho(x2->Mux2) = s1 ^ s0, rho(~x2->Mux2) = ~(s1 ^ s0)
        
        self.edges = [
            # Inputs to MUX 1
            {
                "from": "in_x1", "to": "lit_mux1",
                "rho_str": "~s0",
                "rho_sop": "~s1.~s0 + s1.~s0",
                "rho_eval": lambda s1, s0: int(not s0),
                "description": "Route x1 to Port 1 when s0=0"
            },
            {
                "from": "in_not_x1", "to": "lit_mux1",
                "rho_str": "s0",
                "rho_sop": "~s1.s0 + s1.s0",
                "rho_eval": lambda s1, s0: int(s0),
                "description": "Route ~x1 to Port 1 when s0=1"
            },
            # Inputs to MUX 2
            {
                "from": "in_x2", "to": "lit_mux2",
                "rho_str": "s1 ^ s0",
                "rho_sop": "~s1.s0 + s1.~s0",
                "rho_eval": lambda s1, s0: int(s1 ^ s0),
                "description": "Route x2 to Port 2 when s1 != s0"
            },
            {
                "from": "in_not_x2", "to": "lit_mux2",
                "rho_str": "~(s1 ^ s0)",
                "rho_sop": "~s1.~s0 + s1.s0",
                "rho_eval": lambda s1, s0: int(not (s1 ^ s0)),
                "description": "Route ~x2 to Port 2 when s1 == s0"
            },
            # MUXes to AND Core
            {
                "from": "lit_mux1", "to": "and_core",
                "rho_str": "1",
                "rho_sop": "1",
                "rho_eval": lambda s1, s0: 1,
                "description": "Port 1 literal feed to AND unit"
            },
            {
                "from": "lit_mux2", "to": "and_core",
                "rho_str": "1",
                "rho_sop": "1",
                "rho_eval": lambda s1, s0: 1,
                "description": "Port 2 literal feed to AND unit"
            },
            # AND Core to Accumulator
            {
                "from": "and_core", "to": "acc_core",
                "rho_str": "1",
                "rho_sop": "1",
                "rho_eval": lambda s1, s0: 1,
                "description": "Clause output feed to signed accumulator (Weight = (+1) if ~s1 else (-1))"
            },
            # Accumulator to Comparator
            {
                "from": "acc_core", "to": "decision_cmp",
                "rho_str": "1",
                "rho_sop": "1",
                "rho_eval": lambda s1, s0: 1,
                "description": "Final accumulated sum to threshold comparator"
            }
        ]

    def project(self, s1, s0):
        """
        Projects the CPOG H onto a specific operational scenario (s1, s0).
        Yields active vertices V|s and active edges E|s.
        """
        active_v = [v for v in self.vertices if v["phi_eval"](s1, s0) == 1]
        active_v_ids = set(v["id"] for v in active_v)
        
        active_e = [
            e for e in self.edges
            if e["from"] in active_v_ids and e["to"] in active_v_ids and e["rho_eval"](s1, s0) == 1
        ]
        
        return {
            "scenario": f"{s1}{s0}",
            "active_vertices": active_v,
            "active_edges": active_e
        }

    def evaluate_hardware_datapath(self, X):
        """
        Simulates the hardware execution of the synthesized CPOG datapath across all 4 clause cycles.
        """
        x1, x2 = int(X[0]), int(X[1])
        not_x1, not_x2 = 1 - x1, 1 - x2
        
        input_signals = {
            "in_x1": x1, "in_not_x1": not_x1,
            "in_x2": x2, "in_not_x2": not_x2
        }
        
        accumulated_votes = 0
        cycle_traces = []
        
        for sc in self.scenarios:
            s1, s0 = sc["code"]
            proj = self.project(s1, s0)
            
            # 1. Resolve MUX 1 input
            mux1_val = None
            for e in proj["active_edges"]:
                if e["to"] == "lit_mux1":
                    mux1_val = input_signals[e["from"]]
                    
            # 2. Resolve MUX 2 input
            mux2_val = None
            for e in proj["active_edges"]:
                if e["to"] == "lit_mux2":
                    mux2_val = input_signals[e["from"]]
                    
            # 3. AND Gate Evaluation
            clause_out = mux1_val & mux2_val
            
            # 4. Signed Accumulation
            weight = +1 if s1 == 0 else -1
            accumulated_votes += (clause_out * weight)
            
            cycle_traces.append({
                "scenario": sc["code_str"],
                "clause_name": sc["clause_name"],
                "mux1_val": mux1_val,
                "mux2_val": mux2_val,
                "clause_out": clause_out,
                "weight": weight,
                "running_acc": accumulated_votes
            })
            
        # 5. Final Threshold Comparator (>= 0)
        final_decision = 1 if accumulated_votes >= 0 else 0
        
        return {
            "inputs": list(X),
            "final_decision": final_decision,
            "accumulated_votes": accumulated_votes,
            "cycle_traces": cycle_traces
        }

    def generate_cpog_dot(self):
        lines = []
        lines.append('digraph Synthesized_TM_CPOG {')
        lines.append('  rankdir=TB;')
        lines.append('  splines=ortho;')
        lines.append('  nodesep=0.7;')
        lines.append('  ranksep=0.9;')
        lines.append('  bgcolor="#FFFFFF";')
        lines.append('  fontname="Helvetica,Arial,sans-serif";')
        lines.append('  node [fontname="Helvetica,Arial,sans-serif", shape=box, style="filled,rounded", penwidth=2, margin="0.2,0.1"];')
        lines.append('  edge [fontname="Helvetica,Arial,sans-serif", fontsize=11, penwidth=1.8];')
        lines.append('')
        lines.append('  labelloc="t";')
        lines.append(f'  label="Conditional Partial Order Graph (CPOG) H = (V, E, φ, ρ) for Tsetlin Machine ({self.benchmark_name.upper()})\\n";')
        lines.append('  fontsize=16;')
        lines.append('')

        # Nodes
        node_colors = {
            "input": ("#E0F2FE", "#0284C7"),
            "mux": ("#FEF08A", "#CA8A04"),
            "and_gate": ("#DCFCE7", "#16A34A"),
            "accumulator": ("#F3E8FF", "#9333EA"),
            "comparator": ("#EDE9FE", "#6D28D9")
        }

        for v in self.vertices:
            fill, border = node_colors.get(v["type"], ("#FFFFFF", "#000000"))
            cond_label = f"\\n[φ = {v['phi']}]"
            lines.append(f'  "{v["id"]}" [label="{v["name"]}{cond_label}", fillcolor="{fill}", color="{border}"];')

        lines.append('')
        lines.append('  // Conditional Interconnect Arcs (ρ)')
        for e in self.edges:
            rho_label = f"ρ = {e['rho_str']}"
            edge_color = "#0284C7" if "s0" in e["rho_str"] or "s1" in e["rho_str"] else "#475569"
            lines.append(f'  "{e["from"]}" -> "{e["to"]}" [label="  {rho_label}  ", color="{edge_color}"];')

        lines.append('}')
        return "\n".join(lines)

    def generate_svg(self, svg_path):
        """
        Renders a publication-quality standalone SVG diagram for the synthesized CPOG datapath.
        """
        width = 960
        height = 700
        svg = []
        svg.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="100%" height="100%">')
        svg.append('<defs>')
        svg.append('  <marker id="cpog_arrow" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">')
        svg.append('    <path d="M 0 0 L 10 5 L 0 10 z" fill="#1E293B"/>')
        svg.append('  </marker>')
        svg.append('  <filter id="shadow" x="-5%" y="-5%" width="110%" height="110%">')
        svg.append('    <feDropShadow dx="2" dy="2" stdDeviation="3" flood-opacity="0.15"/>')
        svg.append('  </filter>')
        svg.append('</defs>')

        # Background
        svg.append(f'<rect width="{width}" height="{height}" fill="#F8FAFC" rx="12"/>')
        svg.append(f'<text x="{width/2}" y="35" font-family="Arial, sans-serif" font-size="20" font-weight="bold" fill="#0F172A" text-anchor="middle">Synthesized CPOG Reconfigurable Datapath H = (V, E, φ, ρ)</text>')
        svg.append(f'<text x="{width/2}" y="58" font-family="Arial, sans-serif" font-size="12" fill="#64748B" text-anchor="middle">Unifies 4 Clause Scenarios into 1 Shared Execution Unit with Minimal Boolean Switching Logic</text>')

        # Position layout
        pos = {
            "in_x1": (160, 110), "in_not_x1": (320, 110),
            "in_x2": (640, 110), "in_not_x2": (800, 110),
            "lit_mux1": (240, 240), "lit_mux2": (720, 240),
            "and_core": (480, 360),
            "acc_core": (480, 480),
            "decision_cmp": (480, 600)
        }

        # Draw Conditional Edges
        edges_svg = [
            ("in_x1", "lit_mux1", "ρ = ~s0", "#0284C7", 170, 175),
            ("in_not_x1", "lit_mux1", "ρ = s0", "#0284C7", 310, 175),
            ("in_x2", "lit_mux2", "ρ = s1 ⊕ s0", "#0284C7", 650, 175),
            ("in_not_x2", "lit_mux2", "ρ = ~(s1 ⊕ s0)", "#0284C7", 790, 175),
            ("lit_mux1", "and_core", "ρ = 1", "#475569", 340, 310),
            ("lit_mux2", "and_core", "ρ = 1", "#475569", 620, 310),
            ("and_core", "acc_core", "ρ = 1 (Weight = +1 / -1)", "#9333EA", 490, 425),
            ("acc_core", "decision_cmp", "ρ = 1", "#6D28D9", 490, 545)
        ]

        for src, dst, elabel, ecolor, tx, ty in edges_svg:
            sx, sy = pos[src]
            dx, dy = pos[dst]
            svg.append(f'<path d="M {sx} {sy+25} C {sx} {sy+40}, {dx} {dy-40}, {dx} {dy-25}" fill="none" stroke="{ecolor}" stroke-width="2" marker-end="url(#cpog_arrow)"/>')
            svg.append(f'<rect x="{tx-45}" y="{ty-10}" width="90" height="20" rx="4" fill="#FFFFFF" stroke="{ecolor}" stroke-width="1"/>')
            svg.append(f'<text x="{tx}" y="{ty+4}" font-family="Arial, sans-serif" font-size="10" font-weight="bold" fill="{ecolor}" text-anchor="middle">{elabel}</text>')

        # Draw Units
        units = [
            ("in_x1", "Input Port x1", "Literal x1", "#E0F2FE", "#0284C7", 120, 45),
            ("in_not_x1", "Input Port ~x1", "Literal ~x1", "#E0F2FE", "#0284C7", 120, 45),
            ("in_x2", "Input Port x2", "Literal x2", "#E0F2FE", "#0284C7", 120, 45),
            ("in_not_x2", "Input Port ~x2", "Literal ~x2", "#E0F2FE", "#0284C7", 120, 45),
            ("lit_mux1", "Literal MUX 1", "Select Port 1 [φ=1]", "#FEF08A", "#CA8A04", 150, 50),
            ("lit_mux2", "Literal MUX 2", "Select Port 2 [φ=1]", "#FEF08A", "#CA8A04", 150, 50),
            ("and_core", "Shared AND Core", "2-input Bitwise AND [φ=1]", "#DCFCE7", "#16A34A", 200, 55),
            ("acc_core", "Signed Accumulator", "+1 (s1=0) / -1 (s1=1) [φ=1]", "#F3E8FF", "#9333EA", 220, 55),
            ("decision_cmp", "Threshold Comparator", "Sign Check (Sum >= 0) [φ=1]", "#EDE9FE", "#6D28D9", 220, 55)
        ]

        for uid, title, sub, ufill, ustroke, uw, uh in units:
            cx, cy = pos[uid]
            ux = cx - uw/2
            uy = cy - uh/2
            svg.append(f'<g filter="url(#shadow)">')
            svg.append(f'  <rect x="{ux}" y="{uy}" width="{uw}" height="{uh}" rx="8" fill="{ufill}" stroke="{ustroke}" stroke-width="2"/>')
            svg.append(f'  <text x="{cx}" y="{cy-5}" font-family="Arial, sans-serif" font-size="12" font-weight="bold" fill="#0F172A" text-anchor="middle">{title}</text>')
            svg.append(f'  <text x="{cx}" y="{cy+13}" font-family="Arial, sans-serif" font-size="10" fill="#475569" text-anchor="middle">{sub}</text>')
            svg.append(f'</g>')

        svg.append('</svg>')
        with open(svg_path, "w", encoding="utf-8") as f:
            f.write("\n".join(svg))
        print(f"[4_cpog_synthesis] Standalone CPOG SVG diagram generated: {svg_path}")

    def export_cpog_json(self, json_path):
        data = {
            "benchmark_name": self.benchmark_name,
            "scenario_variables": self.scenario_vars,
            "scenarios": self.scenarios,
            "vertices": self.vertices,
            "edges": [
                {
                    "from": e["from"],
                    "to": e["to"],
                    "rho_str": e["rho_str"],
                    "rho_sop": e["rho_sop"],
                    "description": e["description"]
                }
                for e in self.edges
            ]
        }
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, default=str)
        print(f"[4_cpog_synthesis] CPOG model data exported: {json_path}")

def synthesize_and_save_cpog(tm_model_path="./generated/tm_model.json", output_dir="./generated"):
    os.makedirs(output_dir, exist_ok=True)
    proj_dir = os.path.join(output_dir, "projections")
    os.makedirs(proj_dir, exist_ok=True)
    
    synthesizer = CPOGSynthesizer(tm_model_path)
    
    # 1. Export CPOG DOT
    dot_content = synthesizer.generate_cpog_dot()
    dot_path = os.path.join(output_dir, "cpog_graph.dot")
    with open(dot_path, "w", encoding="utf-8") as f:
        f.write(dot_content)
    print(f"[4_cpog_synthesis] Synthesized CPOG DOT written: {dot_path}")
    
    # 2. Export CPOG SVG
    svg_path = os.path.join(output_dir, "cpog_graph.svg")
    synthesizer.generate_svg(svg_path)
    
    # 3. Export Scenario Projections
    for sc in synthesizer.scenarios:
        s1, s0 = sc["code"]
        proj = synthesizer.project(s1, s0)
        proj_file = os.path.join(proj_dir, f"projection_H_{sc['code_str']}.json")
        with open(proj_file, "w", encoding="utf-8") as f:
            json.dump({
                "scenario": sc,
                "active_vertices": [v["id"] for v in proj["active_vertices"]],
                "active_edges": [{"from": e["from"], "to": e["to"]} for e in proj["active_edges"]]
            }, f, indent=2)
            
    print(f"[4_cpog_synthesis] 4 Scenario Projections exported to: {proj_dir}")
    
    # 4. Export Model JSON
    json_path = os.path.join(output_dir, "cpog_model.json")
    synthesizer.export_cpog_json(json_path)
    
    return synthesizer

if __name__ == "__main__":
    synthesize_and_save_cpog()
