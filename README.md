# Tsetlin Machine to MLIR & CPOG Hardware Reuse Pipeline

> **Automated compilation of Tsetlin Machines into LLVM MLIR SSA IR, Def-Use Dataflow DAG extraction, Conditional Partial Order Graph (CPOG) synthesis, Workcraft formal toolchain integration, and synthesizable Verilog RTL generation.**

[![Status: Verified](https://img.shields.io/badge/Verification-100%25%20Formally%20Proven-brightgreen.svg)](#-formal-verification-results)
[![Compiler: MLIR](https://img.shields.io/badge/IR-LLVM%20MLIR%20SSA-blue.svg)](#stage-2-mlir-compiler)
[![Formal Tool: Workcraft](https://img.shields.io/badge/Tool-Workcraft%203.5.5-orange.svg)](#-workcraft-integration-guide)
[![HDL: Verilog](https://img.shields.io/badge/RTL-IEEE%201364--2005-purple.svg)](#stage-8-synthesizable-verilog-rtl-generation)
[![Reference Paper](https://img.shields.io/badge/Paper-IEEE%20TC%202010-red.svg)](#-academic-literature--reference-papers)

---

## 📖 Executive Summary & Motivation

In conventional spatial (fully unrolled) implementations of the **Tsetlin Machine (TM)**, every learned clause is instantiated as an independent physical circuit in silicon:
- For an $M$-clause model with $N$ inputs, standard hardware allocates $M$ parallel multi-input AND trees and a wide multi-operand adder tree.
- In edge and ultra-low-power scenarios, this creates severe silicon area bloat ($O(M \cdot N)$ literal check gates), high static leakage, and routing interconnect congestion.

### 💡 The Proposed Solution (MLIR Compiler + CPOG Graph Overlay)
1. **Compile Rule-Based Logic to MLIR**: Lowers high-level TM clauses into standard Static Single Assignment (SSA) `func` and `arith` dialect operations.
2. **Extract SSA Dataflow DAG**: Maps operand def-use chains into a computational directed acyclic graph.
3. **Synthesize a Conditional Partial Order Graph (CPOG)**: Uses formal CPOG theory ($H = (V, E, \phi, \rho, S)$) from Mokhov & Yakovlev (IEEE TC 2010) to overlay all $M$ clause subgraphs onto **$K \ll M$ shared, reconfigurable hardware execution cores** controlled by minimal Boolean switching logic.
4. **Formal Verification & RTL Generation**: Mathematically proves structural isomorphism ($H|_S \cong G_{\text{IR}}$) and 100% truth-table behavioral equivalence, then generates cycle-accurate synthesizable Verilog HDL and native Workcraft `.work` models.

---

## ⚡ Quick Start (One-Click Execution)

To execute the entire 8-stage pipeline end-to-end:

### Option 1: Command Line
```bash
python run_full_pipeline.py
```

### Option 2: Windows Batch Script
Double-click `run_pipeline.bat` or run:
```cmd
run_pipeline.bat
```

Execution takes **under 3 seconds** and produces all verified artifacts in the `generated/` directory.

---

## 🏛️ End-to-End 8-Stage Architecture & Codebase

The pipeline consists of 8 automated stages:

| Stage | Script / Module | Description | Outputs Generated |
| :--- | :--- | :--- | :--- |
| **Stage 1** | [`1_simple_tm.py`](./1_simple_tm.py) | Builds and trains the canonical 2-input XOR Tsetlin Machine model (4 clauses: 2 positive, 2 negative). | `generated/tm_model.json` |
| **Stage 2** | [`2_tm_to_mlir.py`](./2_tm_to_mlir.py) | Emits standard lowered MLIR (`arith`/`func` dialects) and domain-specific `tm` dialect; includes built-in SSA interpreter. | `generated/model.mlir`, `generated/model_high_level.mlir` |
| **Stage 3** | [`3_visualize_ir_graph.py`](./3_visualize_ir_graph.py) | Parses MLIR SSA def-use chains and renders vector Dataflow DAGs in Graphviz DOT and SVG formats. | `generated/ir_graph.dot`, `generated/ir_graph.svg`, `generated/ir_graph_data.json` |
| **Stage 4** | [`4_cpog_synthesis.py`](./4_cpog_synthesis.py) | Synthesizes CPOG $H = (V, E, \phi, \rho, S)$, derives minimal Boolean conditions ($\bar{s}_0$, $s_1 \oplus s_0$), and exports scenario projections. | `generated/cpog_graph.dot`, `generated/cpog_graph.svg`, `generated/cpog_model.json`, `generated/projections/` |
| **Stage 5** | [`5_verify_cpog_mlir.py`](./5_verify_cpog_mlir.py) | Formal verification suite proving structural isomorphism ($H|_S \cong G_{\text{IR}}$) and 100% truth-table equivalence across Python TM, MLIR SSA, and CPOG hardware. | `generated/verification_report.json` |
| **Stage 6** | [`6_hardware_reuse_report.py`](./6_hardware_reuse_report.py) | Quantitative hardware reuse analysis (gate count, adder cells, interconnect wires). | `generated/hardware_reuse_report.md`, `generated/hardware_reuse_metrics.json` |
| **Stage 7** | [`7_export_workcraft.py`](./7_export_workcraft.py)<br>[`generate_tm_work.py`](./generate_tm_work.py)<br>[`build_tm_workcraft_work.py`](./build_tm_workcraft_work.py) | Exports native Workcraft CPOG formats (`.g`), SCENCO SAT encoding graphs (`.dot`), and valid binary projects (`.work`) verified via Workcraft engine. | `generated/workcraft_cpog.g`, `generated/workcraft_scenarios.dot`, `generated/workcraft_encoding_spec.json`, `generated/workcraft_cpog.work`, `generated/tsetlin_machine_cpog.work` |
| **Stage 8** | [`8_generate_verilog_rtl.py`](./8_generate_verilog_rtl.py) | Generates IEEE 1364-2005 synthesizable Verilog RTL and a cycle-accurate self-checking testbench. | `generated/tsetlin_machine_cpog.v`, `generated/tb_tsetlin_machine_cpog.v` |

---

## 📐 Mathematical Formulation

### 1. Canonical Tsetlin Machine (Granmo 2018)
For binary input vector $X = (x_1, x_2) \in \{0, 1\}^2$, the literal vector is $L = (x_1, \bar{x}_1, x_2, \bar{x}_2)$:
- **Positive Clauses (Class 1 Votes, $+1$)**:
  $$C_1^+(X) = x_1 \land \bar{x}_2 \quad (\text{detects } [1, 0])$$
  $$C_2^+(X) = \bar{x}_1 \land x_2 \quad (\text{detects } [0, 1])$$
- **Negative Clauses (Class 0 Votes, $-1$)**:
  $$C_1^-(X) = x_1 \land x_2 \quad (\text{detects } [1, 1])$$
  $$C_2^-(X) = \bar{x}_1 \land \bar{x}_2 \quad (\text{detects } [0, 0])$$
- **Voting Tally & Classification**:
  $$\text{Vote}^+ = C_1^+(X) + C_2^+(X), \quad \text{Vote}^- = C_1^-(X) + C_2^-(X)$$
  $$\text{Decision}(X) = \begin{cases} 1 & \text{if } (\text{Vote}^+ - \text{Vote}^-) \ge 0 \\ 0 & \text{otherwise} \end{cases}$$

### 2. Standard MLIR SSA Lowering
The computation is represented in standard LLVM MLIR SSA dialects (`func`, `arith`):
```mlir
module {
  func.func @tsetlin_machine_xor(%x1: i1, %x2: i1) -> i1 {
    %c1_i1 = arith.constant 1 : i1
    %not_x1 = arith.xori %x1, %c1_i1 : i1
    %not_x2 = arith.xori %x2, %c1_i1 : i1

    %c1_pos = arith.andi %x1, %not_x2 : i1
    %c2_pos = arith.andi %not_x1, %x2 : i1
    %c1_neg = arith.andi %x1, %x2 : i1
    %c2_neg = arith.andi %not_x1, %not_x2 : i1

    %c1_p_32 = arith.extui %c1_pos : i1 to i32
    %c2_p_32 = arith.extui %c2_pos : i1 to i32
    %pos_votes = arith.addi %c1_p_32, %c2_p_32 : i32

    %c1_n_32 = arith.extui %c1_neg : i1 to i32
    %c2_n_32 = arith.extui %c2_neg : i1 to i32
    %neg_votes = arith.addi %c1_n_32, %c2_n_32 : i32

    %diff = arith.subi %pos_votes, %neg_votes : i32
    %c0_i32 = arith.constant 0 : i32
    %decision = arith.cmpi sge, %diff, %c0_i32 : i32
    return %decision : i1
  }
}
```

### 3. CPOG Formal Specification (Mokhov & Yakovlev 2010)
A Conditional Partial Order Graph is defined as a 5-tuple $H = (V, E, \phi, \rho, S)$:
- **Operational Scenarios ($S$)**: Controlled by opcode variables $(s_1, s_0) \in \{0, 1\}^2$:
  - $00 \implies C_1^+ \quad (x_1 \land \bar{x}_2)$
  - $01 \implies C_2^+ \quad (\bar{x}_1 \land x_2)$
  - $10 \implies C_1^- \quad (x_1 \land x_2)$
  - $11 \implies C_2^- \quad (\bar{x}_1 \land \bar{x}_2)$
- **Vertex Set ($V$)**: Core execution hardware units:
  - Input literal selectors (`lit_mux1`, `lit_mux2`)
  - Shared AND evaluation core (`and_core`)
  - Signed accumulator (`acc_core`)
  - Threshold comparator (`decision_cmp`)
- **Vertex Activation Conditions ($\phi$)**:
  - $\phi(v_{\text{AND}}) = 1$ (`and_core`: 100% duty cycle across all scenarios)
  - $\phi(v_{\text{ACC}}) = 1$ (`acc_core`: 100% duty cycle)
- **Edge Routing Conditions ($\rho$)**:
  - $\rho(x_1 \to \text{Port}_1) = \bar{s}_0$
  - $\rho(\bar{x}_1 \to \text{Port}_1) = s_0$
  - $\rho(x_2 \to \text{Port}_2) = s_1 \oplus s_0$
  - $\rho(\bar{x}_2 \to \text{Port}_2) = \overline{s_1 \oplus s_0}$
  - Accumulation mode: Add ($+1$) when $s_1 = 0$, Subtract ($-1$) when $s_1 = 1$.

---

## 📊 Key Results & Formal Verification

### 1. Formal Verification Certificate
The verification suite ([`5_verify_cpog_mlir.py`](./5_verify_cpog_mlir.py)) provides two mathematical proofs:

- **Proof 1: Structural Isomorphism ($H|_S \cong G_{\text{IR}}$)**:
  - Scenario `00`: Active inputs `['x1', 'not_x2']` $\iff$ MLIR Clause `x1 & not_x2` $\to$ **PROVEN**
  - Scenario `01`: Active inputs `['not_x1', 'x2']` $\iff$ MLIR Clause `not_x1 & x2` $\to$ **PROVEN**
  - Scenario `10`: Active inputs `['x1', 'x2']` $\iff$ MLIR Clause `x1 & x2` $\to$ **PROVEN**
  - Scenario `11`: Active inputs `['not_x1', 'not_x2']` $\iff$ MLIR Clause `not_x1 & not_x2` $\to$ **PROVEN**

- **Proof 2: Behavioral Truth-Table Equivalence**:
  | Input Vector $(x_1, x_2)$ | Expected Ground Truth | Python TM Model | MLIR SSA Execution | CPOG Synthesized Datapath | Status |
  | :---: | :---: | :---: | :---: | :---: | :---: |
  | `[0, 0]` | **0** | **0** | **0** | **0** | **PASSED** |
  | `[0, 1]` | **1** | **1** | **1** | **1** | **PASSED** |
  | `[1, 0]` | **1** | **1** | **1** | **1** | **PASSED** |
  | `[1, 1]` | **0** | **0** | **0** | **0** | **PASSED** |

### 2. Quantitative Hardware Reuse Metrics (Canonical XOR Benchmark)
| Metric | Spatial Baseline (Unrolled) | Synthesized CPOG (Shared Core) | Concrete Measured Savings |
| :--- | :---: | :---: | :---: |
| **Clause AND2 Gates** | 4 physical gates | **1 shared physical core** | **75.0% Reduction (3 gates eliminated)** |
| **Adder / Accumulator Cells** | 8 Full Adders | **4 Full Adders** | **50.0% Reduction (4 Adders saved)** |
| **Literal Routing Wires** | 8 global wires | **4 local wires** | **50.0% Wiring Reduction** |
| **Hardware Reuse Factor** | $1.0\times$ (No reuse) | **$4.0\times$** | **4 clauses evaluated on 1 shared core** |
| **Control Logic Overhead** | Complex state machine | **Single XOR2 gate ($s_1 \oplus s_0$)** | **Negligible 1-gate Boolean overhead** |

---

## 🛠️ Workcraft Integration Guide

The pipeline exports native formats compatible with Newcastle University's **Workcraft Framework** ([workcraft.org](https://workcraft.org)):

1. **Native Project File (`.work`)**:
   - Open [`generated/workcraft_cpog.work`](./generated/workcraft_cpog.work) directly in Workcraft GUI (`File -> Open...`).
   - Contains the fully styled visual CPOG model with math and visual groups pre-configured.
2. **Native CPOG Format (`.g`)**:
   - Open [`generated/workcraft_cpog.g`](./generated/workcraft_cpog.g) via Workcraft GUI (`File -> Open...`).
   - In the right-hand **Scenarios Panel**, click `C1_pos`, `C2_pos`, `C1_neg`, or `C2_neg` to interactively view scenario projections and highlighted active paths.
3. **SAT-based Optimal Condition Optimization (SCENCO)**:
   - Navigate to **`Tools` $\to$ `Encoding` $\to$ `SAT-based optimal encoding`** to verify that condition formulas are mathematically minimal.
4. **Asynchronous Synthesis**:
   - Synthesize speed-independent asynchronous control circuits using **`Tools` $\to$ `Synthesis` $\to$ `Speed-independent circuit synthesis (Petrify)`**.

---

## 💻 Synthesizable Verilog RTL & Simulation

The synthesized CPOG datapath is generated as cycle-accurate Verilog HDL in [`generated/tsetlin_machine_cpog.v`](./generated/tsetlin_machine_cpog.v) with a self-checking testbench in [`generated/tb_tsetlin_machine_cpog.v`](./generated/tb_tsetlin_machine_cpog.v).

To simulate using Icarus Verilog:
```bash
iverilog -o sim_cpog generated/tsetlin_machine_cpog.v generated/tb_tsetlin_machine_cpog.v
vvp sim_cpog
```

Expected Output:
```text
TEST 1: Input (0,0) -> Output=0 | PASS
TEST 2: Input (0,1) -> Output=1 | PASS
TEST 3: Input (1,0) -> Output=1 | PASS
TEST 4: Input (1,1) -> Output=0 | PASS
ALL TESTS PASSED WITH 100% ACCURACY.
```

---

## 📚 Academic Literature & Reference Papers

The foundational literature studied and synthesized for this CPOG research is archived in [`references_and_papers/`](./references_and_papers/):

| Paper / Resource | File in Repository | Authors / Venue | Key Relevance |
| :--- | :--- | :--- | :--- |
| **Seminal CPOG Theory** | [`Mokhov_2010_IEEE_TC_CPOG.pdf`](./references_and_papers/Mokhov_2010_IEEE_TC_CPOG.pdf)<br>[`Mokhov_2010_IEEE_TC_CPOG_Published.pdf`](./references_and_papers/Mokhov_2010_IEEE_TC_CPOG_Published.pdf) | Andrey Mokhov, Alex Yakovlev<br>*IEEE Transactions on Computers, Vol. 59, No. 5 (2010)* | Seminal paper establishing CPOG mathematical theory $H = (V, E, \phi, \rho, S)$, graph composition, scenario projection, Boolean condition minimization, and microarchitectural datapath overlay. |
| **Foundational Tsetlin Machine** | *arXiv:1804.01508* | Ole-Christoffer Granmo (2018) | Founding paper introducing the Tsetlin Machine propositional logic learning algorithm. |

---

## 🗂️ Project Directory Structure

```text
.
├── 1_simple_tm.py                      # Stage 1: TM model & rule training
├── 2_tm_to_mlir.py                    # Stage 2: MLIR emission & SSA interpreter
├── 3_visualize_ir_graph.py             # Stage 3: SSA Dataflow DAG extraction & SVG rendering
├── 4_cpog_synthesis.py                 # Stage 4: Formal CPOG synthesis & condition minimization
├── 5_verify_cpog_mlir.py               # Stage 5: Formal isomorphism & behavioral verification
├── 6_hardware_reuse_report.py          # Stage 6: Area, gate count, and wire savings report
├── 7_export_workcraft.py              # Stage 7: Workcraft .g and SCENCO .dot exporter
├── 8_generate_verilog_rtl.py          # Stage 8: Synthesizable Verilog RTL & testbench
├── build_tm_workcraft_work.py         # Workcraft .work model packager
├── generate_tm_work.py                # Compliant Workcraft .work XML generator
├── run_full_pipeline.py                # Master 8-stage pipeline orchestrator
├── run_pipeline.bat                   # 1-click Windows execution batch script
├── README.md                           # Project documentation (this file)
├── references_and_papers/              # Academic papers
│   ├── Mokhov_2010_IEEE_TC_CPOG.pdf
│   └── Mokhov_2010_IEEE_TC_CPOG_Published.pdf
└── generated/                          # Generated outputs and artifacts
    ├── tm_model.json                  # Canonical TM rule specifications
    ├── model.mlir                     # Lowered standard MLIR (func, arith)
    ├── model_high_level.mlir          # High-level 'tm' dialect MLIR
    ├── ir_graph.dot & .svg            # Visual SSA Dataflow Graphs
    ├── cpog_graph.dot & .svg          # Visual CPOG Reconfigurable Datapath
    ├── projections/                   # 4 Scenario projections (H|00, H|01, H|10, H|11)
    ├── verification_report.json       # Formal proof certificate
    ├── hardware_reuse_report.md       # Gate area & wire reduction report
    ├── workcraft_cpog.g               # Workcraft native CPOG model
    ├── workcraft_scenarios.dot        # Workcraft SCENCO scenario graph
    ├── workcraft_encoding_spec.json   # Workcraft SAT encoding specification
    ├── workcraft_cpog.work            # Native Workcraft binary project file
    ├── tsetlin_machine_cpog.work      # Standalone Workcraft project file
    ├── tsetlin_machine_cpog.v         # Synthesizable Verilog RTL
    └── tb_tsetlin_machine_cpog.v      # Self-checking testbench
```

---

## 📜 Citation & Attribution

If you use or reference this codebase in your research, please cite the corresponding literature:

```bibtex
@article{mokhov2010cpog,
  author={Mokhov, Andrey and Yakovlev, Alex},
  journal={IEEE Transactions on Computers}, 
  title={Conditional Partial Order Graphs: Model, Synthesis, and Application}, 
  year={2010},
  volume={59},
  number={5},
  pages={700-719}
}

@article{granmo2018tsetlin,
  author={Granmo, Ole-Christoffer},
  title={The Tsetlin Machine - A Game Theoretic, Propositional Logic Approach to Machine Learning},
  journal={arXiv preprint arXiv:1804.01508},
  year={2018}
}
```
