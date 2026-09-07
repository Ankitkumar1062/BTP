# Tsetlin Machine to MLIR & CPOG Hardware Reuse Pipeline

This directory contains the complete implementation, compiler, visualizer, formal verification suite, and hardware reuse analyzer for compiling Tsetlin Machines into MLIR and synthesizing Conditional Partial Order Graphs (CPOG).

---

##  Quick Start (One-Click Execution)

To run the complete 6-stage pipeline and generate all artifacts:

```bash
python run_full_pipeline.py
```

---

##  Codebase Structure

- `1_simple_tm.py`: Canonical Tsetlin Machine model & rule generator (XOR / MUX).
- `2_tm_to_mlir.py`: MLIR code generator (emits standard `func`/`arith` SSA IR + high-level `tm` dialect).
- `3_visualize_ir_graph.py`: Extracts MLIR SSA Dataflow DAG and renders Graphviz DOT & vector SVG diagrams.
- `4_cpog_synthesis.py`: Synthesizes formal CPOG $H = (V, E, \phi, \rho, S)$, derives Boolean switching conditions, and exports scenario projections.
- `5_verify_cpog_mlir.py`: Formal verification engine proving structural isomorphism ($H|_S \cong G_{\text{IR}}$) and 100% truth-table equivalence.
- `6_hardware_reuse_report.py`: Calculates quantitative gate count, area, wire reduction, and large-scale TM scaling metrics.
- `PROJECT_CONTEXT_AND_PROGRESS.md`: **Master research documentation** containing the complete context, literature references (MATADOR, Mokhov IEEE TC 2010), mathematical equations, verification certificates, and future extension guide.

---

## 📊 Key Results

- **Formal Verification**: 100% truth-table accuracy across Python TM, MLIR SSA software simulation, and CPOG hardware execution. All 4 scenario projections are mathematically isomorphic.
- **Hardware Reuse**: Reduces clause AND gates by **75.0%**, reduces adder cells by **50.0%**, and cuts interconnect wiring by **50.0%** for the canonical benchmark (scaling to **>93% area reduction** for 480-clause TMs).
