"""
run_full_pipeline.py
====================
Master orchestrator executing the complete 6-stage Tsetlin Machine to MLIR & CPOG pipeline:

Stage 1: Simple Tsetlin Machine Model & Rules (`1_simple_tm.py`)
Stage 2: MLIR Compiler (`2_tm_to_mlir.py`)
Stage 3: MLIR SSA IR Graph Visualization (`3_visualize_ir_graph.py`)
Stage 4: CPOG Synthesis & Boolean Conditions (`4_cpog_synthesis.py`)
Stage 5: Formal Verification Suite (`5_verify_cpog_mlir.py`)
Stage 6: Hardware Reuse Quantitative Report (`6_hardware_reuse_report.py`)

Run:
  python run_full_pipeline.py
"""

import os
import sys
import time
import importlib

# Ensure script directory is in sys.path
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

def run_pipeline():
    start_time = time.time()
    output_dir = os.path.join(SCRIPT_DIR, "generated")
    os.makedirs(output_dir, exist_ok=True)
    
    print("\n" + "="*80)
    print("      TSETLIN MACHINE -> MLIR -> CPOG HARDWARE REUSE COMPLETE PIPELINE      ")
    print("="*80 + "\n")
    
    # -------------------------------------------------------------------------
    # Stage 1: Simple Tsetlin Machine
    # -------------------------------------------------------------------------
    print(">>> [STAGE 1/6] Building & Training Canonical Tsetlin Machine...")
    tm_mod = importlib.import_module("1_simple_tm")
    tm, tm_model = tm_mod.build_and_save_canonical_tm(output_dir=output_dir, benchmark="xor")
    
    # -------------------------------------------------------------------------
    # Stage 2: TM to MLIR
    # -------------------------------------------------------------------------
    print("\n>>> [STAGE 2/6] Compiling TM to MLIR (Lowered arith/func + High-Level tm)...")
    mlir_mod = importlib.import_module("2_tm_to_mlir")
    emitter = mlir_mod.compile_and_save_mlir(tm_model_path=os.path.join(output_dir, "tm_model.json"), output_dir=output_dir)
    
    # -------------------------------------------------------------------------
    # Stage 3: IR Graph Visualization
    # -------------------------------------------------------------------------
    print("\n>>> [STAGE 3/6] Extracting SSA Dataflow DAG & Generating Visual Graphs (DOT/SVG)...")
    vis_mod = importlib.import_module("3_visualize_ir_graph")
    extractor = vis_mod.visualize_and_save_graphs(tm_model_path=os.path.join(output_dir, "tm_model.json"), output_dir=output_dir)
    
    # -------------------------------------------------------------------------
    # Stage 4: CPOG Synthesis
    # -------------------------------------------------------------------------
    print("\n>>> [STAGE 4/6] Synthesizing Formal CPOG H = (V, E, phi, rho, S) & Projections...")
    cpog_mod = importlib.import_module("4_cpog_synthesis")
    synthesizer = cpog_mod.synthesize_and_save_cpog(tm_model_path=os.path.join(output_dir, "tm_model.json"), output_dir=output_dir)
    
    # -------------------------------------------------------------------------
    # Stage 5: Formal Verification
    # -------------------------------------------------------------------------
    print("\n>>> [STAGE 5/6] Running Formal Isomorphism & Behavioral Verification Suite...")
    verif_mod = importlib.import_module("5_verify_cpog_mlir")
    verifier = verif_mod.FormalVerifier(output_dir=output_dir)
    verif_results = verifier.run_full_verification()
    
    # -------------------------------------------------------------------------
    # Stage 6: Hardware Reuse Analysis
    # -------------------------------------------------------------------------
    print("\n>>> [STAGE 6/6] Computing Quantitative Hardware Reuse Metrics & Scaling...")
    hw_mod = importlib.import_module("6_hardware_reuse_report")
    analyzer = hw_mod.HardwareReuseAnalyzer(output_dir=output_dir)
    canonical_hw, scale_hw = analyzer.run_analysis()
    
    # -------------------------------------------------------------------------
    # Summary of Generated Artifacts
    # -------------------------------------------------------------------------
    elapsed = time.time() - start_time
    print("\n" + "="*80)
    print(f"PIPELINE COMPLETED SUCCESSFULLY IN {elapsed:.2f}s")
    print("="*80)
    print(f"Verification Status : {verif_results['verification_status']}")
    print(f"Generated Artifacts in '{output_dir}':")
    print(f"  1. tm_model.json               : Canonical TM clause definitions & truth table")
    print(f"  2. model.mlir                  : Lowered standard MLIR (func, arith)")
    print(f"  3. model_high_level.mlir       : High-level 'tm' dialect MLIR")
    print(f"  4. ir_graph.dot & .svg         : MLIR SSA IR Dataflow Graphs")
    print(f"  5. cpog_graph.dot & .svg       : Synthesized CPOG Reconfigurable Datapath")
    print(f"  6. projections/                : 4 Individual scenario projection JSONs (H|00, H|01, H|10, H|11)")
    print(f"  7. verification_report.json    : Formal Isomorphism & Truth-Table Proof Certificate")
    print(f"  8. hardware_reuse_report.md    : Full Markdown report on Gate Area & Wire Savings")
    print("="*80 + "\n")

if __name__ == "__main__":
    run_pipeline()
