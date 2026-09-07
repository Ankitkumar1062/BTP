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
        width = 1360
        height = 1320
        svg = []
        svg.append('<?xml version="1.0" encoding="UTF-8"?>')
        svg.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="100%" height="100%">')
        svg.append('<defs>')
        
        # High-Contrast Colored Arrow Markers
        markers = [
            ("arrow-slate", "#475569"),
            ("arrow-blue", "#0284C7"),
            ("arrow-teal", "#0D9488"),
            ("arrow-green", "#16A34A"),
            ("arrow-rose", "#E11D48"),
            ("arrow-amber", "#D97706"),
            ("arrow-purple", "#7C3AED")
        ]
        for mid, mcol in markers:
            svg.append(f'  <marker id="{mid}" viewBox="0 0 10 10" refX="7" refY="5" markerWidth="6" markerHeight="6" orient="auto">')
            svg.append(f'    <path d="M 0 1.5 L 8 5 L 0 8.5 z" fill="{mcol}"/>')
            svg.append('  </marker>')
            
        # Clean Subtle Drop Shadow Filter
        svg.append('  <filter id="card-shadow" x="-8%" y="-8%" width="120%" height="120%">')
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
        
        # Background Canvas
        svg.append(f'<rect width="{width}" height="{height}" fill="#F8FAFC" rx="16"/>')
        
        # Header Banner
        svg.append('<rect x="35" y="20" width="1290" height="75" rx="12" fill="#0F172A"/>')
        svg.append('<text x="680" y="48" font-family="-apple-system, BlinkMacSystemFont, Segoe UI, Roboto, sans-serif" font-size="20" font-weight="700" fill="#F8FAFC" text-anchor="middle">MLIR SSA IR Dataflow Graph (Tsetlin Machine XOR Benchmark)</text>')
        svg.append('<text x="680" y="72" font-family="-apple-system, BlinkMacSystemFont, Segoe UI, Roboto, sans-serif" font-size="12" fill="#94A3B8" text-anchor="middle">Multi-Level Intermediate Representation (MLIR) Static Single Assignment (SSA) Def-Use Dataflow Graph</text>')

        # ---------------------------------------------------------------------
        # Stage Clusters Panels (With 35px+ Header Padding to Prevent Card Overlap)
        # ---------------------------------------------------------------------
        stage_clusters = [
            (35, 110, 1290, 160, "STAGE 0: PRIMARY INPUTS &amp; LITERAL INVERSION (arith.xori)", "#F8FAFC", "#CBD5E1", "#0284C7"),
            (35, 390, 1290, 180, "STAGE 1: CLAUSE CONJUNCTION TREES (arith.andi)", "#F8FAFC", "#CBD5E1", "#16A34A"),
            (35, 600, 1290, 180, "STAGE 2: VOTING ACCUMULATION TREES (arith.extui &amp; arith.addi)", "#F8FAFC", "#CBD5E1", "#D97706"),
            (35, 810, 1290, 360, "STAGE 3: SUBTRACTION &amp; THRESHOLD COMPARISON (arith.subi &amp; arith.cmpi)", "#F8FAFC", "#CBD5E1", "#7C3AED")
        ]
        
        for bx, by, bw, bh, blabel, bfill, bstroke, baccent in stage_clusters:
            svg.append(f'<rect x="{bx}" y="{by}" width="{bw}" height="{bh}" rx="12" fill="{bfill}" stroke="{bstroke}" stroke-width="1.5"/>')
            svg.append(f'<rect x="{bx}" y="{by}" width="6" height="{bh}" rx="3" fill="{baccent}"/>')
            svg.append(f'<text x="{bx+20}" y="{by+28}" font-family="-apple-system, BlinkMacSystemFont, Segoe UI, Roboto, sans-serif" font-size="12" font-weight="700" fill="#334155" letter-spacing="0.5">{blabel}</text>')

        # ---------------------------------------------------------------------
        # Directed Routing Paths (Multi-Level Bus to Prevent Any Arrow Overlap)
        # ---------------------------------------------------------------------
        edges = [
            # Inverter horizontal connections in Stage 0 (y=205)
            ("M 305 205 L 360 205", "arrow-teal", "#0D9488", 2.0, "%x1"),
            ("M 915 205 L 970 205", "arrow-teal", "#0D9488", 2.0, "%x2"),

            # Stage 0 -> Stage 1: Literals into Clauses
            # 1. x1 -> C1_pos (Straight drop)
            ("M 160 245 L 160 440", "arrow-blue", "#0284C7", 2.0, "%x1"),
            
            # 2. x1 -> C1_neg (High Bus Layer at y=295)
            ("M 240 245 C 240 295, 770 295, 770 440", "arrow-blue", "#0284C7", 2.0, "%x1"),

            # 3. not_x1 -> C2_pos (Direct drop)
            ("M 430 245 C 430 310, 450 330, 450 440", "arrow-teal", "#0D9488", 2.0, "%not_x1"),

            # 4. not_x1 -> C2_neg (Mid Bus Layer at y=325)
            ("M 510 245 C 510 325, 1060 325, 1060 440", "arrow-teal", "#0D9488", 2.0, "%not_x1"),

            # 5. x2 -> C2_pos (Leftward curve at y=345)
            ("M 770 245 C 770 345, 530 345, 530 440", "arrow-blue", "#0284C7", 2.0, "%x2"),

            # 6. x2 -> C1_neg (Direct drop)
            ("M 850 245 C 850 310, 850 330, 850 440", "arrow-blue", "#0284C7", 2.0, "%x2"),

            # 7. not_x2 -> C1_pos (Low Bus Layer at y=365)
            ("M 1040 245 C 1040 365, 240 365, 240 440", "arrow-teal", "#0D9488", 2.0, "%not_x2"),

            # 8. not_x2 -> C2_neg (Direct drop)
            ("M 1120 245 C 1120 310, 1140 330, 1140 440", "arrow-teal", "#0D9488", 2.0, "%not_x2"),

            # Stage 1 -> Stage 2: Clauses into Vote Adders (Enter at y=650, WELL BELOW Stage 2 Header at y=628)
            # Positive Accumulator Tree (Left Half)
            ("M 200 540 C 200 595, 270 610, 270 650", "arrow-green", "#16A34A", 2.4, "%c1_pos"),
            ("M 490 540 C 490 595, 420 610, 420 650", "arrow-green", "#16A34A", 2.4, "%c2_pos"),

            # Negative Accumulator Tree (Right Half)
            ("M 810 540 C 810 595, 880 610, 880 650", "arrow-rose", "#E11D48", 2.4, "%c1_neg"),
            ("M 1100 540 C 1100 595, 1030 610, 1030 650", "arrow-rose", "#E11D48", 2.4, "%c2_neg"),

            # Stage 2 -> Stage 3: Adders into Subtractor (Enter at y=867, WELL BELOW Stage 3 Header at y=838)
            ("M 345 750 C 345 810, 540 825, 540 867", "arrow-amber", "#D97706", 2.4, "%pos_votes"),
            ("M 955 750 C 955 810, 760 825, 760 867", "arrow-amber", "#D97706", 2.4, "%neg_votes"),

            # Subtractor to Comparator (Straight Vertical: y=962 to y=997)
            ("M 650 962 L 650 997", "arrow-purple", "#7C3AED", 2.6, "%diff"),
            
            # Comparator to Return Port (y=1092 to y=1130)
            ("M 650 1092 L 650 1130", "arrow-purple", "#7C3AED", 2.6, "%decision")
        ]

        for d_path, mark, scolor, swidth, elabel in edges:
            svg.append(f'<path d="{d_path}" fill="none" stroke="{scolor}" stroke-width="{swidth}" marker-end="url(#{mark})"/>')

        # ---------------------------------------------------------------------
        # Node Cards with Precise, Non-Overlapping Internal Geometry
        # ---------------------------------------------------------------------
        cards = [
            # Stage 0 (cy=205, h=80 -> ry=165 to 245, Header at y=138. Clearance = 27px)
            ("x1", 200, 205, 210, 80, "Primary Input: x1", "Argument %x1 : i1", "input.arg", "#EFF6FF", "#3B82F6", "#DBEAFE", "#1E40AF"),
            ("not_x1", 470, 205, 210, 80, "Inverter: NOT x1", "arith.xori %x1, 1", "%not_x1 : i1", "#F0FDFA", "#14B8A6", "#CCFBF1", "#115E59"),
            ("x2", 810, 205, 210, 80, "Primary Input: x2", "Argument %x2 : i1", "input.arg", "#EFF6FF", "#3B82F6", "#DBEAFE", "#1E40AF"),
            ("not_x2", 1080, 205, 210, 80, "Inverter: NOT x2", "arith.xori %x2, 1", "%not_x2 : i1", "#F0FDFA", "#14B8A6", "#CCFBF1", "#115E59"),

            # Stage 1 (cy=490, h=100 -> ry=440 to 540, Header at y=418. Clearance = 22px)
            ("c1_pos", 200, 490, 240, 100, "Clause C1+ (Pos Vote +1)", "Formula: x1 &amp; ~x2", "arith.andi %x1, %not_x2 : i1", "#F0FDF4", "#22C55E", "#DCFCE7", "#166534"),
            ("c2_pos", 490, 490, 240, 100, "Clause C2+ (Pos Vote +1)", "Formula: ~x1 &amp; x2", "arith.andi %not_x1, %x2 : i1", "#F0FDF4", "#22C55E", "#DCFCE7", "#166534"),
            ("c1_neg", 810, 490, 240, 100, "Clause C1- (Neg Vote -1)", "Formula: x1 &amp; x2", "arith.andi %x1, %x2 : i1", "#FFF1F2", "#F43F5E", "#FFE4E6", "#9F1239"),
            ("c2_neg", 1100, 490, 240, 100, "Clause C2- (Neg Vote -1)", "Formula: ~x1 &amp; ~x2", "arith.andi %not_x1, %not_x2 : i1", "#FFF1F2", "#F43F5E", "#FFE4E6", "#9F1239"),

            # Stage 2 (cy=700, h=100 -> ry=650 to 750, Header at y=628. Clearance = 22px)
            ("pos_votes", 345, 700, 370, 100, "Positive Vote Accumulator (+Votes)", "arith.addi %c1_pos_ext, %c2_pos_ext", "%pos_votes : i32 (Zero-Extended)", "#FFFBEB", "#F59E0B", "#FEF3C7", "#92400E"),
            ("neg_votes", 955, 700, 370, 100, "Negative Vote Accumulator (-Votes)", "arith.addi %c1_neg_ext, %c2_neg_ext", "%neg_votes : i32 (Zero-Extended)", "#FFFBEB", "#F59E0B", "#FEF3C7", "#92400E"),

            # Stage 3 (Subtractor: cy=915, h=95 -> ry=867.5 to 962.5, Header at y=838. Clearance = 29.5px)
            ("diff", 650, 915, 390, 95, "Vote Difference Subtractor", "arith.subi %pos_votes, %neg_votes", "%diff = (+Votes) - (-Votes) : i32", "#FAF5FF", "#A855F7", "#F3E8FF", "#6B21A8"),
            
            # Stage 3 (Comparator: cy=1045, h=95 -> ry=997.5 to 1092.5)
            ("decision", 650, 1045, 390, 95, "Threshold Decision Comparator", "arith.cmpi sge, %diff, 0", "Output: (%diff &gt;= 0) ? 1 : 0 (i1)", "#F5F3FF", "#8B5CF6", "#EDE9FE", "#5B21B6")
        ]

        for cid, cx, cy, cw, ch, title, formula, dialect_tag, cfill, cstroke, tag_fill, tag_text in cards:
            rx_pos = cx - cw/2
            ry_pos = cy - ch/2
            
            svg.append(f'<g filter="url(#card-shadow)">')
            svg.append(f'  <rect x="{rx_pos}" y="{ry_pos}" width="{cw}" height="{ch}" rx="10" fill="{cfill}" stroke="{cstroke}" stroke-width="2"/>')
            
            # Title (Clean top positioning)
            svg.append(f'  <text x="{cx}" y="{ry_pos+24}" font-family="-apple-system, BlinkMacSystemFont, Segoe UI, Roboto, sans-serif" font-size="12" font-weight="700" fill="#0F172A" text-anchor="middle">{title}</text>')
            
            # Formula / Subtitle (Middle positioning)
            svg.append(f'  <text x="{cx}" y="{ry_pos+46}" font-family="-apple-system, BlinkMacSystemFont, Segoe UI, Roboto, sans-serif" font-size="11" font-weight="500" fill="#475569" text-anchor="middle">{formula}</text>')
            
            # MLIR Dialect Code Pill Badge (Bottom positioning with zero collision)
            badge_w = cw - 28
            badge_h = 22
            badge_x = cx - badge_w/2
            badge_y = ry_pos + ch - 30
            svg.append(f'  <rect x="{badge_x}" y="{badge_y}" width="{badge_w}" height="{badge_h}" rx="5" fill="{tag_fill}"/>')
            svg.append(f'  <text x="{cx}" y="{badge_y+15}" font-family="Consolas, Monaco, monospace" font-size="10" font-weight="600" fill="{tag_text}" text-anchor="middle">{dialect_tag}</text>')
            svg.append(f'</g>')

        # Footer Legend
        svg.append('<rect x="35" y="1195" width="1290" height="95" rx="10" fill="#FFFFFF" stroke="#E2E8F0" stroke-width="1.5"/>')
        svg.append('<text x="55" y="1222" font-family="-apple-system, BlinkMacSystemFont, Segoe UI, Roboto, sans-serif" font-size="11" font-weight="700" fill="#475569">GRAPH LEGEND &amp; BUS LAYERS:</text>')
        
        legend_items = [
            (210, 1222, "#3B82F6", "Primary Inputs (i1)"),
            (380, 1222, "#14B8A6", "Inverters (xori)"),
            (550, 1222, "#22C55E", "Pos Clauses (+1)"),
            (720, 1222, "#F43F5E", "Neg Clauses (-1)"),
            (890, 1222, "#F59E0B", "Vote Adders (addi)"),
            (1070, 1222, "#8B5CF6", "Comparator (cmpi)")
        ]
        for lx, ly, lcol, ltext in legend_items:
            svg.append(f'<circle cx="{lx}" cy="{ly-4}" r="6" fill="{lcol}"/>')
            svg.append(f'<text x="{lx+12}" y="{ly}" font-family="-apple-system, BlinkMacSystemFont, Segoe UI, Roboto, sans-serif" font-size="11" fill="#334155">{ltext}</text>')
            
        svg.append('<text x="680" y="1255" font-family="-apple-system, BlinkMacSystemFont, Segoe UI, Roboto, sans-serif" font-size="11" fill="#64748B" text-anchor="middle">Dataflow: Top-to-Bottom SSA evaluation. Multi-level horizontal buses (y=295, y=325, y=365) and generous stage padding guarantee zero overlap.</text>')

        svg.append('</svg>')
        with open(svg_path, "w", encoding="utf-8") as f:
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
