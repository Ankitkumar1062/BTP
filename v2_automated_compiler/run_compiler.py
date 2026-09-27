import argparse
import os

from importlib.machinery import SourceFileLoader

# Dynamically load the modules
simple_tm = SourceFileLoader("simple_tm", "./1_simple_tm.py").load_module()
tm_to_mlir = SourceFileLoader("tm_to_mlir", "./2_tm_to_mlir.py").load_module()
cpog_synthesis = SourceFileLoader("cpog_synthesis", "./4_cpog_synthesis.py").load_module()
export_workcraft = SourceFileLoader("export_workcraft", "./7_export_workcraft.py").load_module()
generate_tm_work = SourceFileLoader("generate_tm_work", "./generate_tm_work.py").load_module()

def main():
    parser = argparse.ArgumentParser(description="V2 Automated Tsetlin-to-CPOG Compiler")
    parser.add_argument("--dataset", type=str, choices=["xor", "iris"], default="xor", help="Dataset to compile (xor or iris)")
    parser.add_argument("--max_alus", type=int, default=1, help="Hardware constraint: Max number of parallel AND Cores")
    parser.add_argument("--optimize_logic", type=bool, default=False, help="Enable Algebraic Logic Optimization (C+ to deduce C-)")
    
    args = parser.parse_args()
    
    print("\n" + "="*60)
    print(">>> AUTOMATED TSETLIN-TO-CPOG COMPILER STARTING <<<")
    print(f"Dataset:            {args.dataset.upper()}")
    print(f"Hardware Max ALUs:  {args.max_alus}")
    print(f"Logic Optimization: {'Enabled' if args.optimize_logic else 'Disabled'}")
    print("="*60 + "\n")
    
    output_dir = "./generated"
    os.makedirs(output_dir, exist_ok=True)
    
    # 1. Build Model
    print(">>> Phase 1: Machine Learning Model Generation")
    simple_tm.build_and_save_canonical_tm(output_dir, args.dataset)
    print("")
    
    # 2. Emit MLIR
    print(">>> Phase 2: Compiler Optimization & MLIR Generation")
    emitter = tm_to_mlir.AutomatedMLIREmitter(f"{output_dir}/tm_model.json", max_alus=args.max_alus, optimize_logic=args.optimize_logic)
    emitter.emit_lowered_mlir(f"{output_dir}/model_{args.max_alus}alu.mlir")
    print("")
    
    # 3. Synthesize CPOG
    print(">>> Phase 3: Automated Boolean Logic Solver & CPOG Synthesis")
    synth = cpog_synthesis.AutomatedCPOGSynthesizer(f"{output_dir}/tm_model.json", max_alus=args.max_alus, optimize_logic=args.optimize_logic)
    synth.export_cpog_model(f"{output_dir}/cpog_model.json")
    print("")
    
    # 4. Export Workcraft
    print(">>> Phase 4: EDA Toolchain (Workcraft) Generation")
    # We will pass the specific output names so we don't overwrite if we run multiple times
    g_path = os.path.join(output_dir, f"workcraft_{args.dataset}_{args.max_alus}alu.g")
    
    exporter = export_workcraft.WorkcraftCPOGExporter(output_dir)
    exporter.export_workcraft_g_format(g_path)
    
    # 5. Generate Native .work Archive
    work_path = f"workcraft_{args.dataset}_{args.max_alus}alu.work"
    generate_tm_work.create_work_files(output_dir, "cpog_model.json", work_path)
    
    print(f"\n[SUCCESS] COMPILATION COMPLETE! Generated Workcraft file: {os.path.join(output_dir, work_path)}\n")

if __name__ == "__main__":
    main()
