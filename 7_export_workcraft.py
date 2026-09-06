"""
7_export_workcraft.py
=====================
Workcraft CPOG Plugin & SCENCO Exporter.

Exports the synthesized CPOG model into native Workcraft-compatible formats:
1. `generated/workcraft_cpog.g` : Native Workcraft CPOG format.
2. `generated/workcraft_scenarios.dot` : Scenario-encoded graph for Workcraft SCENCO plugin.
3. `generated/workcraft_encoding_spec.json` : SAT-based encoding variables and scenario table.

Tool Integration:
- Open in Workcraft GUI (https://workcraft.org) via:
  File -> Open -> workcraft_cpog.g
- Or run Workcraft CLI for automated SAT-based condition optimization:
  workcraft -exec:cpog-sat-encode generated/workcraft_cpog.g
"""

import os
import json

class WorkcraftCPOGExporter:
    """
    Exports CPOG models to Workcraft and SCENCO formats.
    """
    def __init__(self, output_dir="./generated"):
        self.output_dir = output_dir
        self.cpog_model_path = os.path.join(output_dir, "cpog_model.json")
        with open(self.cpog_model_path, "r", encoding="utf-8") as f:
            self.model = json.load(f)

    def export_workcraft_g_format(self, out_path):
        """
        Emits Workcraft '.g' format for Conditional Partial Order Graphs.
        """
        lines = []
        lines.append("# Workcraft CPOG Model Specification")
        lines.append(f"# Benchmark: {self.model['benchmark_name'].upper()} Tsetlin Machine")
        lines.append(f"# Scenario Variables: {', '.join(self.model['scenario_variables'])}")
        lines.append(".model cpog_tsetlin_machine")
        lines.append("")
        
        # Declare variables
        lines.append(f".inputs {' '.join(self.model['scenario_variables'])}")
        lines.append("")
        
        # Vertices with conditions phi(v)
        lines.append("# Vertices and Activation Conditions phi(v)")
        for v in self.model["vertices"]:
            lines.append(f".vertex {v['id']} [label=\"{v['name']}\"] [cond=\"{v['phi']}\"]")
            
        lines.append("")
        # Arcs with conditions rho(e)
        lines.append("# Directed Arcs and Routing Conditions rho(e)")
        for e in self.model["edges"]:
            lines.append(f".arc {e['from']} -> {e['to']} [cond=\"{e['rho_str']}\"] [sop=\"{e['rho_sop']}\"]")
            
        lines.append("")
        # Scenarios / Opcodes
        lines.append("# Operational Scenarios (Opcodes)")
        for sc in self.model["scenarios"]:
            lines.append(f"# Scenario {sc['code_str']} -> {sc['clause_name']} ({sc['formula']})")
            lines.append(f".scenario {sc['clause_name']} s1={sc['code'][0]} s0={sc['code'][1]}")
            
        lines.append(".end")
        
        with open(out_path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
        print(f"[7_export_workcraft] Workcraft native .g format written: {out_path}")

    def export_scenco_dot(self, out_path):
        """
        Emits Workcraft SCENCO scenario-encoded DOT graph.
        """
        lines = []
        lines.append('digraph Workcraft_SCENCO_TM {')
        lines.append('  graph [name="CPOG_Tsetlin_Machine", variables="s1,s0"];')
        lines.append('  node [shape=box, style="filled,rounded", fontname="Helvetica"];')
        lines.append('  edge [fontname="Helvetica", fontsize=10];')
        lines.append('')
        
        for v in self.model["vertices"]:
            lines.append(f'  "{v["id"]}" [label="{v["name"]}", condition="{v["phi"]}"];')
            
        lines.append('')
        for e in self.model["edges"]:
            rho_cond = e["rho_str"]
            rho_sop = e["rho_sop"]
            lines.append(f'  "{e["from"]}" -> "{e["to"]}" [condition="{rho_cond}", sop="{rho_sop}"];')
            
        lines.append('}')
        
        with open(out_path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
        print(f"[7_export_workcraft] Workcraft SCENCO DOT format written: {out_path}")

    def export_sat_spec(self, out_path):
        """
        Exports machine-readable SAT encoding specification.
        """
        spec = {
            "model_type": "Conditional Partial Order Graph (CPOG)",
            "encoding_engine": "Workcraft SCENCO SAT-based Optimal Encoder",
            "control_variables": self.model["scenario_variables"],
            "num_scenarios": len(self.model["scenarios"]),
            "scenarios": self.model["scenarios"],
            "synthesized_conditions": {
                "vertex_conditions": {v["id"]: v["phi"] for v in self.model["vertices"]},
                "edge_conditions": [
                    {
                        "arc": f"{e['from']} -> {e['to']}",
                        "boolean_condition": e["rho_str"],
                        "sum_of_products": e["rho_sop"]
                    }
                    for e in self.model["edges"]
                ]
            }
        }
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(spec, f, indent=2)
        print(f"[7_export_workcraft] SAT encoding specification saved: {out_path}")

def run_workcraft_export(output_dir="./generated"):
    os.makedirs(output_dir, exist_ok=True)
    exporter = WorkcraftCPOGExporter(output_dir)
    
    g_path = os.path.join(output_dir, "workcraft_cpog.g")
    exporter.export_workcraft_g_format(g_path)
    
    dot_path = os.path.join(output_dir, "workcraft_scenarios.dot")
    exporter.export_scenco_dot(dot_path)
    
    sat_path = os.path.join(output_dir, "workcraft_encoding_spec.json")
    exporter.export_sat_spec(sat_path)

if __name__ == "__main__":
    run_workcraft_export()
