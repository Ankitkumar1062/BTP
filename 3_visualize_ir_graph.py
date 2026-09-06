"""
3_visualize_ir_graph.py
=======================
Extracts the SSA Dataflow Directed Acyclic Graph (DAG) from the MLIR instruction stream.

Outputs:
1. `generated/ir_graph.dot`: Graphviz DOT representation styled with clustered computation stages.
2. `generated/ir_graph.svg`: Rendered standalone vector SVG diagram for direct visual inspection.
3. `generated/ir_graph_data.json`: Structural graph metadata (nodes & edges) for formal verification.
"""

import os
import json
import subprocess
import shutil

class MLIRGraphExtractor:
    """
    Constructs and visualizes the MLIR SSA Dataflow Graph.
    """
    def __init__(self, tm_model_path="./generated/tm_model.json"):
        with open(tm_model_path, "r") as f:
            self.model = json.load(f)
            
        self.benchmark_name = self.model["benchmark_name"]
        self.num_inputs = self.model["num_inputs"]
        self.clauses = self.model["clauses"]
        
        self.nodes = []
        self.edges = []
        self._build_graph()

    def _build_graph(self):
        # 1. Inputs (Stage 0)
        for i in range(1, self.num_inputs + 1):
            self.nodes.append({
                "id": f"x{i}",
                "label": f"Input x{i}\\n(i1)",
                "stage": "inputs",
                "type": "input",
                "fillcolor": "#E1F5FE",
                "color": "#0288D1"
            })
            
        # 2. Inverters (Stage 0 - Literals)
        for i in range(1, self.num_inputs + 1):
            nid = f"not_x{i}"
            self.nodes.append({
                "id": nid,
                "label": f"NOT Gate\\n~x{i} (xori %x{i}, 1)",
                "stage": "literals",
                "type": "inverter",
                "fillcolor": "#E0F2F1",
                "color": "#00796B"
            })
            self.edges.append({
                "from": f"x{i}",
                "to": nid,
                "label": f"%x{i}"
            })

        # 3. Clause Conjunctions (Stage 1)
        for c in self.clauses:
            cname = c["clause_name"].lower()
            pol_str = "Pos (+1)" if c["polarity"] == +1 else "Neg (-1)"
            formula_str = c["formula"]
            fill = "#E8F5E9" if c["polarity"] == +1 else "#FFEBEE"
            border = "#2E7D32" if c["polarity"] == +1 else "#C62828"
            
            self.nodes.append({
                "id": cname,
                "label": f"Clause {c['clause_name']}\\n[{pol_str}]\\nAND: {formula_str}",
                "stage": "clauses",
                "type": "clause_and",
                "polarity": c["polarity"],
                "fillcolor": fill,
                "color": border
            })
            
            for lit in c["included_literals"]:
                self.edges.append({
                    "from": lit,
                    "to": cname,
                    "label": f"%{lit}"
                })

        # 4. Voting & Accumulation (Stage 2)
        pos_clauses = [c["clause_name"].lower() for c in self.clauses if c["polarity"] == +1]
        neg_clauses = [c["clause_name"].lower() for c in self.clauses if c["polarity"] == -1]
        
        # Pos Adder
        self.nodes.append({
            "id": "pos_votes",
            "label": "Positive Vote Adder\\n(arith.addi %c1_pos, %c2_pos)\\n[+Votes : i32]",
            "stage": "voting",
            "type": "adder",
            "fillcolor": "#FFF3E0",
            "color": "#E65100"
        })
        for pc in pos_clauses:
            self.edges.append({
                "from": pc,
                "to": "pos_votes",
                "label": f"%{pc}_ext"
            })

        # Neg Adder
        self.nodes.append({
            "id": "neg_votes",
            "label": "Negative Vote Adder\\n(arith.addi %c1_neg, %c2_neg)\\n[-Votes : i32]",
            "stage": "voting",
            "type": "adder",
            "fillcolor": "#FFF3E0",
            "color": "#E65100"
        })
        for nc in neg_clauses:
            self.edges.append({
                "from": nc,
                "to": "neg_votes",
                "label": f"%{nc}_ext"
            })

        # 5. Subtractor & Comparator (Stage 3)
        self.nodes.append({
            "id": "diff",
            "label": "Vote Subtractor\\n(arith.subi %pos_votes, %neg_votes)\\n[%diff : i32]",
            "stage": "decision",
            "type": "subtractor",
            "fillcolor": "#F3E5F5",
            "color": "#7B1FA2"
        })
        self.edges.append({"from": "pos_votes", "to": "diff", "label": "%pos_votes"})
        self.edges.append({"from": "neg_votes", "to": "diff", "label": "%neg_votes"})

        self.nodes.append({
            "id": "decision",
            "label": "Threshold Comparator\\n(arith.cmpi sge, %diff, 0)\\n[Output %decision : i1]",
            "stage": "decision",
            "type": "comparator",
            "fillcolor": "#EDE7F6",
            "color": "#4A148C"
        })
        self.edges.append({"from": "diff", "to": "decision", "label": "%diff >= 0"})

    def generate_dot(self):
        lines = []
        lines.append('digraph MLIR_Tsetlin_Machine_Dataflow {')
        lines.append('  rankdir=TB;')
        lines.append('  splines=ortho;')
        lines.append('  nodesep=0.6;')
        lines.append('  ranksep=0.8;')
        lines.append('  bgcolor="#FFFFFF";')
        lines.append('  fontname="Helvetica,Arial,sans-serif";')
        lines.append('  node [fontname="Helvetica,Arial,sans-serif", shape=box, style="filled,rounded", penwidth=2, margin="0.2,0.1"];')
        lines.append('  edge [fontname="Helvetica,Arial,sans-serif", fontsize=10, color="#455A64", penwidth=1.5];')
        lines.append('')
        lines.append('  // Title')
        lines.append('  labelloc="t";')
        lines.append(f'  label="MLIR SSA IR Dataflow Graph for Tsetlin Machine ({self.benchmark_name.upper()} Benchmark)\\n";')
        lines.append('  fontsize=16;')
        lines.append('')

        # Group by clusters
        stages = {
            "inputs": ("Primary Inputs", "#FAFAFA", "#B0BEC5"),
            "literals": ("Stage 0: Literal Generation (Inverters)", "#ECEFF1", "#90A4AE"),
            "clauses": ("Stage 1: Clause Conjunction Trees", "#F1F8E9", "#AED581"),
            "voting": ("Stage 2: Voting & Accumulation Tree", "#FFFDE7", "#FFF59D"),
            "decision": ("Stage 3: Threshold Decision & Output", "#EDE7F6", "#D1C4E9")
        }

        for st_key, (st_label, bg_col, border_col) in stages.items():
            lines.append(f'  subgraph cluster_{st_key} {{')
            lines.append(f'    label="{st_label}";')
            lines.append(f'    style="filled,rounded";')
            lines.append(f'    bgcolor="{bg_col}";')
            lines.append(f'    color="{border_col}";')
            lines.append(f'    fontsize=12;')
            
            for n in self.nodes:
                if n["stage"] == st_key:
                    lines.append(f'    "{n["id"]}" [label="{n["label"]}", fillcolor="{n["fillcolor"]}", color="{n["color"]}"];')
            lines.append('  }')
            lines.append('')

        # Edges
        lines.append('  // SSA Def-Use Edges')
        for e in self.edges:
            lines.append(f'  "{e["from"]}" -> "{e["to"]}" [label=" {e["label"]} "];')
            
        lines.append('}')
        return "\n".join(lines)

    def generate_svg(self, dot_path, svg_path):
        """
        Attempts rendering via Graphviz 'dot' if available; otherwise falls back to a clean standalone SVG renderer.
        """
        dot_bin = shutil.which("dot")
        if dot_bin:
            try:
                subprocess.run([dot_bin, "-Tsvg", dot_path, "-o", svg_path], check=True)
                print(f"[3_visualize_ir_graph] Graphviz 'dot' rendered SVG: {svg_path}")
                return
            except Exception as e:
                print(f"Graphviz run failed ({e}), generating custom SVG fallback.")

        # Standalone vector SVG generator
        self._generate_custom_svg(svg_path)

    def _generate_custom_svg(self, svg_path):
        width = 1000
        height = 800
        svg = []
        svg.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="100%" height="100%">')
        svg.append('<defs>')
        svg.append('  <marker id="arrow" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">')
        svg.append('    <path d="M 0 0 L 10 5 L 0 10 z" fill="#37474F"/>')
        svg.append('  </marker>')
        svg.append('  <filter id="shadow" x="-5%" y="-5%" width="110%" height="110%">')
        svg.append('    <feDropShadow dx="2" dy="2" stdDeviation="3" flood-opacity="0.15"/>')
        svg.append('  </filter>')
        svg.append('</defs>')
        
        # Background
        svg.append(f'<rect width="{width}" height="{height}" fill="#F8FAFC" rx="12"/>')
        svg.append(f'<text x="{width/2}" y="40" font-family="Arial, sans-serif" font-size="22" font-weight="bold" fill="#0F172A" text-anchor="middle">MLIR SSA IR Dataflow Graph (Tsetlin Machine {self.benchmark_name.upper()})</text>')
        svg.append(f'<text x="{width/2}" y="65" font-family="Arial, sans-serif" font-size="13" fill="#64748B" text-anchor="middle">Static Single Assignment (SSA) Representation with Dialect Operations</text>')

        # Node positions map (Layered)
        pos = {
            "x1": (220, 120), "x2": (680, 120),
            "not_x1": (380, 120), "not_x2": (840, 120),
            "c1_pos": (180, 260), "c2_pos": (420, 260),
            "c1_neg": (660, 260), "c2_neg": (900, 260),
            "pos_votes": (300, 430), "neg_votes": (780, 430),
            "diff": (540, 560),
            "decision": (540, 690)
        }

        # Draw Stage Clusters
        stage_boxes = [
            (100, 85, 860, 95, "Stage 0: Primary Inputs & Inverted Literals", "#F1F5F9", "#CBD5E1"),
            (80, 205, 900, 140, "Stage 1: Clause Conjunction Trees (AND Reductions)", "#F0FDF4", "#BBF7D0"),
            (180, 370, 700, 130, "Stage 2: Voting & Accumulation Tree (ADD)", "#FEFCE8", "#FEF08A"),
            (360, 520, 360, 220, "Stage 3: Subtraction & Threshold Decision", "#FAF5FF", "#E9D5FF")
        ]
        for bx, by, bw, bh, blabel, bfill, bstroke in stage_boxes:
            svg.append(f'<rect x="{bx}" y="{by}" width="{bw}" height="{bh}" rx="8" fill="{bfill}" stroke="{bstroke}" stroke-width="1.5"/>')
            svg.append(f'<text x="{bx+15}" y="{by+20}" font-family="Arial, sans-serif" font-size="12" font-weight="bold" fill="#475569">{blabel}</text>')

        # Draw Edges
        edge_coords = [
            ("x1", "not_x1", "%x1"), ("x2", "not_x2", "%x2"),
            ("x1", "c1_pos", "%x1"), ("not_x2", "c1_pos", "%not_x2"),
            ("not_x1", "c2_pos", "%not_x1"), ("x2", "c2_pos", "%x2"),
            ("x1", "c1_neg", "%x1"), ("x2", "c1_neg", "%x2"),
            ("not_x1", "c2_neg", "%not_x1"), ("not_x2", "c2_neg", "%not_x2"),
            ("c1_pos", "pos_votes", "%c1_pos"), ("c2_pos", "pos_votes", "%c2_pos"),
            ("c1_neg", "neg_votes", "%c1_neg"), ("c2_neg", "neg_votes", "%c2_neg"),
            ("pos_votes", "diff", "%pos_votes"), ("neg_votes", "diff", "%neg_votes"),
            ("diff", "decision", "%diff")
        ]
        for src, dst, elabel in edge_coords:
            if src in pos and dst in pos:
                sx, sy = pos[src]
                dx, dy = pos[dst]
                svg.append(f'<path d="M {sx} {sy+25} C {sx} {sy+50}, {dx} {dy-50}, {dx} {dy-25}" fill="none" stroke="#475569" stroke-width="1.8" marker-end="url(#arrow)"/>')

        # Draw Nodes
        node_styles = {
            "x1": ("Input x1", "Primary Input i1", "#E0F2FE", "#0284C7", 130, 50),
            "x2": ("Input x2", "Primary Input i1", "#E0F2FE", "#0284C7", 130, 50),
            "not_x1": ("NOT x1", "arith.xori %x1, 1", "#CCFBF1", "#0D9488", 130, 50),
            "not_x2": ("NOT x2", "arith.xori %x2, 1", "#CCFBF1", "#0D9488", 130, 50),
            "c1_pos": ("Clause C1_pos (+)", "x1 & ~x2", "#DCFCE7", "#16A34A", 140, 60),
            "c2_pos": ("Clause C2_pos (+)", "~x1 & x2", "#DCFCE7", "#16A34A", 140, 60),
            "c1_neg": ("Clause C1_neg (-)", "x1 & x2", "#FFE4E6", "#E11D48", 140, 60),
            "c2_neg": ("Clause C2_neg (-)", "~x1 & ~x2", "#FFE4E6", "#E11D48", 140, 60),
            "pos_votes": ("+ Vote Adder", "arith.addi : i32", "#FEF08A", "#CA8A04", 170, 55),
            "neg_votes": ("- Vote Adder", "arith.addi : i32", "#FEF08A", "#CA8A04", 170, 55),
            "diff": ("Vote Subtractor", "arith.subi : i32", "#F3E8FF", "#9333EA", 180, 55),
            "decision": ("Threshold Comparator", "arith.cmpi sge, %diff, 0", "#EDE9FE", "#6D28D9", 200, 55)
        }

        for nid, (title, sub, nfill, nstroke, nw, nh) in node_styles.items():
            cx, cy = pos[nid]
            nx = cx - nw/2
            ny = cy - nh/2
            svg.append(f'<g filter="url(#shadow)">')
            svg.append(f'  <rect x="{nx}" y="{ny}" width="{nw}" height="{nh}" rx="8" fill="{nfill}" stroke="{nstroke}" stroke-width="2"/>')
            svg.append(f'  <text x="{cx}" y="{cy-5}" font-family="Arial, sans-serif" font-size="12" font-weight="bold" fill="#0F172A" text-anchor="middle">{title}</text>')
            svg.append(f'  <text x="{cx}" y="{cy+14}" font-family="Arial, sans-serif" font-size="10" fill="#475569" text-anchor="middle">{sub}</text>')
            svg.append(f'</g>')

        svg.append('</svg>')
        with open(svg_path, "w") as f:
            f.write("\n".join(svg))
        print(f"[3_visualize_ir_graph] Standalone vector SVG generated: {svg_path}")

    def export_graph_json(self, json_path):
        data = {
            "benchmark_name": self.benchmark_name,
            "nodes": self.nodes,
            "edges": self.edges
        }
        with open(json_path, "w") as f:
            json.dump(data, f, indent=2)
        print(f"[3_visualize_ir_graph] Graph structural data saved: {json_path}")

def visualize_and_save_graphs(tm_model_path="./generated/tm_model.json", output_dir="./generated"):
    os.makedirs(output_dir, exist_ok=True)
    extractor = MLIRGraphExtractor(tm_model_path)
    
    # Export DOT
    dot_content = extractor.generate_dot()
    dot_path = os.path.join(output_dir, "ir_graph.dot")
    with open(dot_path, "w") as f:
        f.write(dot_content)
    print(f"[3_visualize_ir_graph] Graphviz DOT file written: {dot_path}")
    
    # Export SVG
    svg_path = os.path.join(output_dir, "ir_graph.svg")
    extractor.generate_svg(dot_path, svg_path)
    
    # Export JSON
    json_path = os.path.join(output_dir, "ir_graph_data.json")
    extractor.export_graph_json(json_path)
    
    return extractor

if __name__ == "__main__":
    visualize_and_save_graphs()
