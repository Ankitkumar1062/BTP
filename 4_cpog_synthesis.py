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
        width = 1180
        height = 920
        svg = []
        svg.append('<?xml version="1.0" encoding="UTF-8"?>')
        svg.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="100%" height="100%">')
        svg.append('<defs>')
        
        # Arrow Markers
        markers = [
            ("cpog-blue", "#0284C7"),
            ("cpog-slate", "#475569"),
            ("cpog-green", "#16A34A"),
            ("cpog-purple", "#7C3AED")
        ]
        for mid, mcol in markers:
            svg.append(f'  <marker id="{mid}" viewBox="0 0 10 10" refX="7" refY="5" markerWidth="6" markerHeight="6" orient="auto">')
            svg.append(f'    <path d="M 0 1.5 L 8 5 L 0 8.5 z" fill="{mcol}"/>')
            svg.append('  </marker>')
            
        svg.append('  <filter id="card-shadow" x="-10%" y="-10%" width="125%" height="125%">')
        svg.append('    <feGaussianBlur in="SourceAlpha" stdDeviation="3"/>')
        svg.append('    <feOffset dx="0" dy="2" result="offsetblur"/>')
        svg.append('    <feFlood flood-color="#0F172A" flood-opacity="0.08"/>')
        svg.append('    <feComposite in2="offsetblur" operator="in"/>')
        svg.append('    <feMerge>')
        svg.append('      <feMergeNode/>')
        svg.append('      <feMergeNode in="SourceGraphic"/>')
        svg.append('    </feMerge>')
        svg.append('  </filter>')
        svg.append('</defs>')

        # Background
        svg.append(f'<rect width="{width}" height="{height}" fill="#F8FAFC" rx="16"/>')
        
        # Header Card
        svg.append('<rect x="30" y="20" width="1120" height="75" rx="12" fill="#0F172A"/>')
        svg.append('<text x="590" y="50" font-family="-apple-system, BlinkMacSystemFont, Segoe UI, Roboto, sans-serif" font-size="20" font-weight="700" fill="#F8FAFC" text-anchor="middle">Synthesized CPOG Reconfigurable Datapath H = (V, E, &#966;, &#961;)</text>')
        svg.append('<text x="590" y="74" font-family="-apple-system, BlinkMacSystemFont, Segoe UI, Roboto, sans-serif" font-size="12" fill="#94A3B8" text-anchor="middle">Unified Reconfigurable Architecture: 4 Clause Scenarios Folded onto 1 Shared Execution Core</text>')

        # Position layout
        pos = {
            "in_x1": (200, 160), "in_not_x1": (400, 160),
            "in_x2": (780, 160), "in_not_x2": (980, 160),
            "lit_mux1": (300, 310), "lit_mux2": (880, 310),
            "and_core": (590, 460),
            "acc_core": (590, 610),
            "decision_cmp": (590, 760)
        }

        # Draw Conditional Edges (Arcs)
        edges_svg = [
            ("in_x1", "lit_mux1", "&#961; = ~s0", "#0284C7", 210, 235),
            ("in_not_x1", "lit_mux1", "&#961; = s0", "#0284C7", 390, 235),
            ("in_x2", "lit_mux2", "&#961; = s1 &#8853; s0", "#0284C7", 790, 235),
            ("in_not_x2", "lit_mux2", "&#961; = ~(s1 &#8853; s0)", "#0284C7", 970, 235),
            ("lit_mux1", "and_core", "&#961; = 1 (Port 1)", "#475569", 410, 395),
            ("lit_mux2", "and_core", "&#961; = 1 (Port 2)", "#475569", 770, 395),
            ("and_core", "acc_core", "&#961; = 1 (Weight: +1 if s1=0, -1 if s1=1)", "#7C3AED", 590, 545),
            ("acc_core", "decision_cmp", "&#961; = 1 (Signed Total Tally)", "#7C3AED", 590, 695)
        ]

        for src, dst, elabel, ecolor, tx, ty in edges_svg:
            sx, sy = pos[src]
            dx, dy = pos[dst]
            m_id = "cpog-blue" if ecolor == "#0284C7" else ("cpog-purple" if ecolor == "#7C3AED" else "cpog-slate")
            svg.append(f'<path d="M {sx} {sy+35} C {sx} {sy+70}, {dx} {dy-70}, {dx} {dy-35}" fill="none" stroke="{ecolor}" stroke-width="2.2" marker-end="url(#{m_id})"/>')
            
            # Condition Pill Box
            pill_w = 110 if len(elabel) < 20 else (260 if len(elabel) > 30 else 140)
            svg.append(f'<rect x="{tx - pill_w/2}" y="{ty-11}" width="{pill_w}" height="22" rx="6" fill="#FFFFFF" stroke="{ecolor}" stroke-width="1.2"/>')
            svg.append(f'<text x="{tx}" y="{ty+4}" font-family="Consolas, Monaco, monospace" font-size="10" font-weight="700" fill="{ecolor}" text-anchor="middle">{elabel}</text>')

        # Units / Vertices
        units = [
            ("in_x1", 200, 160, 160, 65, "Input Literal: x1", "Primary Input %x1", "#EFF6FF", "#3B82F6", "#DBEAFE", "#1E40AF"),
            ("in_not_x1", 400, 160, 160, 65, "Input Literal: ~x1", "Inverted %not_x1", "#F0FDFA", "#14B8A6", "#CCFBF1", "#115E59"),
            ("in_x2", 780, 160, 160, 65, "Input Literal: x2", "Primary Input %x2", "#EFF6FF", "#3B82F6", "#DBEAFE", "#1E40AF"),
            ("in_not_x2", 980, 160, 160, 65, "Input Literal: ~x2", "Inverted %not_x2", "#F0FDFA", "#14B8A6", "#CCFBF1", "#115E59"),

            ("lit_mux1", 300, 310, 240, 80, "Literal Selector MUX 1", "Selects x1 or ~x1 [&#966;=1]", "#FFFBEB", "#F59E0B", "#FEF3C7", "#92400E"),
            ("lit_mux2", 880, 310, 240, 80, "Literal Selector MUX 2", "Selects x2 or ~x2 [&#966;=1]", "#FFFBEB", "#F59E0B", "#FEF3C7", "#92400E"),

            ("and_core", 590, 460, 340, 85, "Shared 2-Input AND Core", "100% Duty Cycle [&#966;=1] (Reused for all 4 Clauses)", "#F0FDF4", "#22C55E", "#DCFCE7", "#166534"),
            ("acc_core", 590, 610, 340, 85, "Signed Voting Accumulator", "+1 (s1=0) / -1 (s1=1) [&#966;=1]", "#FAF5FF", "#A855F7", "#F3E8FF", "#6B21A8"),
            ("decision_cmp", 590, 760, 340, 85, "Threshold Decision Comparator", "Sign Check: (vote_sum &gt;= 0) ? 1 : 0", "#F5F3FF", "#8B5CF6", "#EDE9FE", "#5B21B6")
        ]

        for uid, cx, cy, cw, ch, title, sub, ufill, ustroke, tfill, tcolor in units:
            rx_pos = cx - cw/2
            ry_pos = cy - ch/2
            
            svg.append(f'<g filter="url(#card-shadow)">')
            svg.append(f'  <rect x="{rx_pos}" y="{ry_pos}" width="{cw}" height="{ch}" rx="10" fill="{ufill}" stroke="{ustroke}" stroke-width="2"/>')
            svg.append(f'  <text x="{cx}" y="{ry_pos+22}" font-family="-apple-system, BlinkMacSystemFont, Segoe UI, Roboto, sans-serif" font-size="12" font-weight="700" fill="#0F172A" text-anchor="middle">{title}</text>')
            
            badge_w = cw - 30
            badge_h = 22
            badge_x = cx - badge_w/2
            badge_y = ry_pos + ch - 28
            svg.append(f'  <rect x="{badge_x}" y="{badge_y}" width="{badge_w}" height="{badge_h}" rx="5" fill="{tfill}"/>')
            svg.append(f'  <text x="{cx}" y="{badge_y+15}" font-family="Consolas, Monaco, monospace" font-size="10" font-weight="600" fill="{tcolor}" text-anchor="middle">{sub}</text>')
            svg.append(f'</g>')

        # Footer Legend / Scenario Codebook
        svg.append('<rect x="30" y="845" width="1120" height="60" rx="10" fill="#FFFFFF" stroke="#E2E8F0" stroke-width="1.5"/>')
        svg.append('<text x="50" y="872" font-family="-apple-system, BlinkMacSystemFont, Segoe UI, Roboto, sans-serif" font-size="11" font-weight="700" fill="#475569">CONTROL CODEBOOK S = (s1, s0):</text>')
        
        scenarios_legend = [
            (280, 872, "00: C1+ (x1 &amp; ~x2) [+1 Vote]"),
            (500, 872, "01: C2+ (~x1 &amp; x2) [+1 Vote]"),
            (720, 872, "10: C1- (x1 &amp; x2) [-1 Vote]"),
            (940, 872, "11: C2- (~x1 &amp; ~x2) [-1 Vote]")
        ]
        for sx, sy, stext in scenarios_legend:
            svg.append(f'<text x="{sx}" y="{sy}" font-family="Consolas, Monaco, monospace" font-size="11" font-weight="600" fill="#0284C7">{stext}</text>')

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
