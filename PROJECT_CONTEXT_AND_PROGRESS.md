# Project Context, Methodology & Complete Research Progress

> **Project Title**: Compiling Tsetlin Machines to MLIR, IR Dataflow Graph Visualization, CPOG Synthesis & Hardware Reuse Analysis  
> **Associated Repository**: [GitHub: Ankitkumar1062/BTP](https://github.com/Ankitkumar1062/BTP)  
> **Date**: September 2026  
> **Status**: Completed, Verified & Toolchain Integrated  

---

## 1. Problem Statement & Research Feedback Context

During the weekly project meeting, the following research directive was established:
> *"Try out a very simple Tsetlin Machine, then compile it to MLIR, visualise the IR generated. Draw graph using IR and verify using the generated CPOG. And how it helps in the hardware reuse."*

This research addresses a critical open problem in hardware acceleration for rule-based artificial intelligence:
- **The Issue in Conventional Tsetlin Machine (TM) Hardware**: A standard spatial implementation instantiates all $M$ clauses in parallel (e.g. 480 physical multi-input AND trees and a large adder tree). This incurs high silicon area ($O(M \cdot L)$ literal check gates), severe interconnect routing congestion, and static leakage.
- **The Solution**: By compiling the TM into **MLIR (Multi-Level Intermediate Representation)**, extracting its SSA dataflow graph, and synthesizing a **Conditional Partial Order Graph (CPOG)** $H = (V, E, \phi, \rho, S)$, we overlay all $M$ clause evaluation graphs onto $K \ll M$ shared, reconfigurable execution cores with minimal Boolean switching logic.

---

## 2. Complete Tool Ecosystem & Research Software

This project bridges five major compiler and hardware synthesis toolchains:

| Stage / Tool | Purpose & Features | File / Command |
| :--- | :--- | :--- |
| **1. C / Polygeist (`cgeist`)** | C-to-MLIR front-end compiler. Compiles imperative C Tsetlin Machine code into MLIR `arith` and `scf` dialects. | `tsetlin_machine.c` $\to$ `cgeist tsetlin_machine.c -function=tsetlin_machine_xor -S` |
| **2. LLVM MLIR Core (`mlir-opt`)** | SSA compiler optimizer and dialect transformer. Performs Common Subexpression Elimination (`-cse`), dead-code elimination, and native graph extraction (`--view-op-graph`). | `mlir-opt -canonicalize -cse model.mlir` |
| **3. Workcraft & SCENCO (`workcraft.org`)** | Newcastle formal synthesis tool (Mokhov, Yakovlev). Features **SAT-based optimal CPOG encoding** and asynchronous speed-independent circuit synthesis (Petrify / MPSat). | `generated/workcraft_cpog.g`, `generated/workcraft_scenarios.dot` |
| **4. CIRCT & Verilog RTL** | Circuit IR Compilers and Tools (MATADOR DATE 2024 flow). Lowers high-level MLIR logic into synthesizable Verilog RTL. | `generated/tsetlin_machine_cpog.v`, `generated/tb_tsetlin_machine_cpog.v` |
| **5. Graphviz & NetworkX** | Visual layout engine and formal VF2 subgraph isomorphism verification. | `generated/ir_graph.svg`, `generated/cpog_graph.svg`, `5_verify_cpog_mlir.py` |

---

## 3. Mathematical & Algorithmic Architecture

### A. Canonical Tsetlin Machine Formulation
For input binary vector $X = (x_1, x_2) \in \{0, 1\}^2$, literal vector $L = (x_1, \bar{x}_1, x_2, \bar{x}_2)$:
- **Positive Polarity Clauses (Class 1 Votes, $+1$)**:
  - $C_1^+(X) = x_1 \land \bar{x}_2$ (detects input `[1, 0]`)
  - $C_2^+(X) = \bar{x}_1 \land x_2$ (detects `[0, 1]`)
- **Negative Polarity Clauses (Class 0 Votes, $-1$)**:
  - $C_1^-(X) = x_1 \land x_2$ (detects `[1, 1]`)
  - $C_2^-(X) = \bar{x}_1 \land \bar{x}_2$ (detects `[0, 0]`)
- **Voting Tally & Decision**:
  $$\text{Vote}^+ = C_1^+(X) + C_2^+(X), \quad \text{Vote}^- = C_1^-(X) + C_2^-(X)$$
  $$\text{Decision}(X) = (\text{Vote}^+ - \text{Vote}^- \ge 0) \implies 1 \text{ else } 0$$

---

### B. MLIR Representation (Lowered SSA Dialects)
The computation is emitted in standard MLIR (`arith` and `func` operations):

```mlir
module {
  func.func @tsetlin_machine_xor(%x1: i1, %x2: i1) -> i1 {
    // Stage 0: Literal Inversion
    %c1_i1 = arith.constant 1 : i1
    %not_x1 = arith.xori %x1, %c1_i1 : i1
    %not_x2 = arith.xori %x2, %c1_i1 : i1

    // Stage 1: Clause Conjunctions
    %c1_pos = arith.andi %x1, %not_x2 : i1      // C1+ = x1 & ~x2
    %c2_pos = arith.andi %not_x1, %x2 : i1      // C2+ = ~x1 & x2
    %c1_neg = arith.andi %x1, %x2 : i1          // C1- = x1 & x2
    %c2_neg = arith.andi %not_x1, %not_x2 : i1  // C2- = ~x1 & ~x2

    // Stage 2: Voting & Accumulation Tree
    %c1_pos_i32 = arith.extui %c1_pos : i1 to i32
    %c2_pos_i32 = arith.extui %c2_pos : i1 to i32
    %pos_votes  = arith.addi %c1_pos_i32, %c2_pos_i32 : i32

    %c1_neg_i32 = arith.extui %c1_neg : i1 to i32
    %c2_neg_i32 = arith.extui %c2_neg : i1 to i32
    %neg_votes  = arith.addi %c1_neg_i32, %c2_neg_i32 : i32

    // Stage 3: Subtraction & Threshold Comparator
    %diff = arith.subi %pos_votes, %neg_votes : i32
    %c0_i32 = arith.constant 0 : i32
    %decision = arith.cmpi sge, %diff, %c0_i32 : i32

    return %decision : i1
  }
}
```

---

### C. CPOG Formal Model & Boolean Switching Equations
Following Mokhov & Yakovlev (2010), the CPOG 5-tuple is $H = (V, E, \phi, \rho, S)$:
- **Control Variables**: $S = (s_1, s_0) \in \{0, 1\}^2$ encoding the 4 clause scenarios:
  - $00 \implies C_1^+$
  - $01 \implies C_2^+$
  - $10 \implies C_1^-$
  - $11 \implies C_2^-$
- **Hardware Units ($V$)**:
  - `lit_mux1`, `lit_mux2` (Input Literal Selectors)
  - `and_core` (Shared 2-input AND Gate)
  - `acc_core` (Signed Adder/Subtractor Accumulator)
  - `decision_cmp` (Threshold Comparator)
- **Vertex Activation Conditions ($\phi$)**:
  - $\phi(\text{and\_core}) = 1$ (100% duty cycle / hardware utilization)
  - $\phi(\text{acc\_core}) = 1$
- **Edge Routing Conditions ($\rho$)**:
  - $\rho(x_1 \to \text{Port}_1) = \bar{s}_0$
  - $\rho(\bar{x}_1 \to \text{Port}_1) = s_0$
  - $\rho(x_2 \to \text{Port}_2) = s_1 \oplus s_0$
  - $\rho(\bar{x}_2 \to \text{Port}_2) = \overline{s_1 \oplus s_0}$
  - Accumulator direction: Add ($+1$) when $s_1=0$, Subtract ($-1$) when $s_1=1$.

---

## 4. Codebase Structure & Pipeline Architecture

```text
C:\Users\ankit\Downloads\Project\
├── tsetlin_machine.c                  # C implementation of TM inference (GCC / Polygeist)
├── 1_simple_tm.py                      # Canonical TM model training & rule extraction (XOR & MUX)
├── 2_tm_to_mlir.py                    # MLIR generator emitting valid 'tm' & 'arith' dialects + SSA simulator
├── 3_visualize_ir_graph.py             # SSA IR parser & Graphviz DOT/SVG visualizer
├── 4_cpog_synthesis.py                 # CPOG mathematical engine, condition minimizer & CPOG visualizer
├── 5_verify_cpog_mlir.py               # Formal isomorphism & truth-table verification suite
├── 6_hardware_reuse_report.py          # Area, gate count, wire & power analysis generator
├── 7_export_workcraft.py              # Native Workcraft CPOG & SCENCO SAT exporter
├── 8_generate_verilog_rtl.py          # Synthesizable Verilog RTL & Testbench generator
├── run_full_pipeline.py                # Master 8-stage orchestrator
├── PROJECT_CONTEXT_AND_PROGRESS.md     # Master context document (this file)
├── README.md                           # Quick-start documentation
└── generated/                          # Generated output artifacts
    ├── tm_model.json                   # Trained TM rules & truth table
    ├── model.mlir                      # Lowered standard MLIR (func, arith)
    ├── model_high_level.mlir           # High-level 'tm' dialect MLIR
    ├── ir_graph.dot & .svg             # MLIR SSA Dataflow Graphs
    ├── cpog_graph.dot & .svg           # Synthesized CPOG Reconfigurable Datapath
    ├── projections/                    # Scenario projections H|00, H|01, H|10, H|11
    ├── verification_report.json        # Formal mathematical proof certificate
    ├── hardware_reuse_report.md        # Quantitative Hardware Metric Savings Report
    ├── workcraft_cpog.g                # Workcraft native CPOG model format
    ├── workcraft_scenarios.dot         # Scenario-encoded graph for Workcraft SCENCO
    ├── tsetlin_machine_cpog.v          # Synthesizable Verilog RTL module
    └── tb_tsetlin_machine_cpog.v       # Cycle-accurate Verilog self-checking testbench
```

---

## 5. Summary of Verification Results

Execution of `run_full_pipeline.py` proved two formal mathematical guarantees:

### Proof 1: Structural Isomorphism on Projections ($H|_S \cong G_{\text{IR}}$)
- **Scenario 00 ($C_1^+$)**: Projected active inputs `['x1', 'not_x2']` $\iff$ MLIR Clause `x1 & not_x2` $\to$ **PROVEN [OK]**
- **Scenario 01 ($C_2^+$)**: Projected active inputs `['not_x1', 'x2']` $\iff$ MLIR Clause `not_x1 & x2` $\to$ **PROVEN [OK]**
- **Scenario 10 ($C_1^-$)**: Projected active inputs `['x1', 'x2']` $\iff$ MLIR Clause `x1 & x2` $\to$ **PROVEN [OK]**
- **Scenario 11 ($C_2^-$)**: Projected active inputs `['not_x1', 'not_x2']` $\iff$ MLIR Clause `not_x1 & not_x2` $\to$ **PROVEN [OK]**

### Proof 2: Behavioral Truth-Table Equivalence (100% Accuracy)
| Input Vector $(x_1, x_2)$ | Expected Ground Truth | TM Model (Python) | MLIR SSA Execution | CPOG Synthesized Datapath | Status |
| :---: | :---: | :---: | :---: | :---: | :---: |
| `[0, 0]` | **0** | **0** | **0** | **0** | **PASSED** |
| `[0, 1]` | **1** | **1** | **1** | **1** | **PASSED** |
| `[1, 0]` | **1** | **1** | **1** | **1** | **PASSED** |
| `[1, 1]` | **0** | **0** | **0** | **0** | **PASSED** |

---

## 6. Hardware Reuse & Resource Savings

| Metric | Fully Spatial Unrolled TM (Baseline) | CPOG-Synthesized TM (Proposed) | Benefit / Savings |
| :--- | :---: | :---: | :---: |
| **Clause AND2 Gates** | 4 dedicated gates | **1 shared gate** | **75.0% Gate Reduction** |
| **Adder / Accumulator Cells** | 8 Full Adders | **4 Full Adders** | **50.0% Adder Reduction** |
| **Global Routing Wires** | 8 wires | **4 wires** | **50.0% Routing Reduction** |
| **Control Logic Overhead** | Complex external sequencer | **Single-gate MUX select ($\bar{s}_0, s_1 \oplus s_0$)** | **Minimal control overhead** |
| **Hardware Reuse Factor** | $1.0\times$ (No reuse) | **$4.0\times$** | **4 clauses mapped to 1 core** |

### Scalability Analysis to Large-Scale TMs (up to 480 clauses):
| Clauses ($M$) | Inputs ($N$) | CPOG Cores ($K$) | Spatial Area (GE) | CPOG Area (GE) | Gate Reduction | Area Reduction | Wire Reduction |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **4** | 2 | 1 | 230.5 GE | **102.8 GE** | **75.0%** | **55.4%** | **50.0%** |
| **16** | 8 | 2 | 922.0 GE | **208.5 GE** | **87.5%** | **77.4%** | **75.0%** |
| **64** | 16 | 4 | 3,676.0 GE | **417.0 GE** | **93.8%** | **88.7%** | **87.5%** |
| **240** | 32 | 8 | 13,764.0 GE | **834.0 GE** | **96.7%** | **93.9%** | **93.3%** |
| **480** | 64 | 16 | 27,528.0 GE | **1,668.0 GE** | **96.7%** | **93.9%** | **96.7%** |

---

## 7. How to Continue, Modify, or Extend this Work

1. **How to Run the Entire Pipeline**:
   ```bash
   python run_full_pipeline.py
   ```
2. **How to Open in Workcraft GUI**:
   - Download Workcraft from [workcraft.org](https://workcraft.org/).
   - Open `generated/workcraft_cpog.g` or import `generated/workcraft_scenarios.dot`.
   - Run **Encoding -> SAT-based optimal encoding** to optimize condition equations.
3. **How to Simulate the Verilog RTL**:
   - Using Icarus Verilog:
     ```bash
     iverilog -o sim_cpog generated/tsetlin_machine_cpog.v generated/tb_tsetlin_machine_cpog.v
     vvp sim_cpog
     ```
