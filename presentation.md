<!-- SLIDE 1 -->
## Slide 1: Objectives & Progress Overview

# Tsetlin Machine to MLIR & CPOG Hardware Reuse
### Project Progress & Implementation Walkthrough

- **Student:** Ankit Kumar *(BTP Project)*
- **Objectives from Previous Meeting:**
  1. Implement a simple Tsetlin Machine model.
  2. Compile it into MLIR compiler IR and visualize the generated IR graph.
  3. Synthesize a CPOG (Conditional Partial Order Graph) based on reference literature.
  4. Show how the CPOG enables hardware reuse.
  5. Integrate with the Workcraft tool and verify the CPOG against the IR.

> **How to Explain:**  
> *"Good morning. Following our previous meeting, our goals were: to implement a simple Tsetlin Machine, compile it to MLIR, draw the dataflow graph from the IR, apply CPOG graph theory from the Mokhov & Yakovlev paper to see how hardware can be reused, inspect the model in Workcraft, and verify that the CPOG behaves consistently with the IR. In this presentation, I will walk through what we did for each of these steps."*

---

<!-- SLIDE 2 -->
## Slide 2: Task 1 - Implementing a Simple Tsetlin Machine

- **What We Did:**
  - Implemented the canonical 2-input XOR benchmark model.
  - Takes binary inputs ($x_1, x_2$) and automatically generates complemented literals ($\bar{x}_1, \bar{x}_2$).
- **Extracted Logic Clauses:**
  - **Positive Clauses (Vote for Class 1):**
    - $C_1^+ = x_1 \land \bar{x}_2$ (detects pattern `[1, 0]`)
    - $C_2^+ = \bar{x}_1 \land x_2$ (detects pattern `[0, 1]`)
  - **Negative Clauses (Vote for Class 0):**
    - $C_1^- = x_1 \land x_2$ (detects pattern `[1, 1]`)
    - $C_2^- = \bar{x}_1 \land \bar{x}_2$ (detects pattern `[0, 0]`)
- **Decision Rule:**
  - Subtracts negative votes from positive votes to make the final classification.

> **How to Explain:**  
> *"As discussed in our meeting, we started with a very simple Tsetlin Machine: the 2-input XOR benchmark. It consists of 4 propositional logic rules: two positive clauses and two negative clauses. Each clause performs a simple bitwise AND on the inputs, and the sum of positive versus negative votes determines the final output."*

---

<!-- SLIDE 3 -->
## Slide 3: Task 2 - Compiling the Model to MLIR

- **What We Did:**
  - Lowered the extracted Tsetlin logic rules into standard **LLVM MLIR**.
  - Uses modern compiler intermediate representation to keep the flow structured and vendor-independent.
- **Mapping Logic to Standard Dialects:**
  - **Inversions:** `arith.xori` computes bitwise NOT for complements ($\bar{x}_1, \bar{x}_2$).
  - **Clause Evaluation:** `arith.andi` evaluates literal AND conditions for each clause.
  - **Voting Tally:** `arith.addi` and `arith.subi` aggregate clause outputs into signed sums.
  - **Decision:** `arith.cmpi` compares the final tally against zero.
- **Execution:**
  - Built an MLIR SSA interpreter to execute and test the compiled IR directly.

> **How to Explain:**  
> *"Next, we compiled the Tsetlin logic into LLVM MLIR using standard arithmetic operations. Literal inversions are mapped to XOR, clauses to bitwise AND, and voting to integer additions and subtractions. We also built an SSA interpreter to run and validate the compiled code directly at the compiler level."*

---

<!-- SLIDE 4 -->
## Slide 4: Task 3 - Visualizing the IR Graph (Dataflow DAG)

- **What We Did:**
  - Parsed the MLIR SSA def-use chains to track how operands flow between operations.
  - Automatically constructed a computational **Directed Acyclic Graph (DAG)**.
- **What the Graph Reveals:**
  - Clearly displays how inputs branch into inversions.
  - Shows which literals connect into the 4 clause evaluation nodes.
  - Illustrates the convergence into the voting addition tree and comparator.
- **Outcome:**
  - Generates a clear vector visualization of the complete computation flow, providing the topological blueprint for hardware synthesis.

> 🖼️ **Visual for this Slide:**  
> Insert diagram: [`generated/ir_graph.svg`](./generated/ir_graph.svg) *(shows top inputs, NOT branches, 4 clause AND nodes, and adder tree)*.

> **How to Explain:**  
> *"To visualize the generated IR, we parsed the def-use chains in MLIR. This traces where every value originates and where it is consumed, automatically building a Directed Acyclic Graph. As shown in the diagram on this slide, it provides a clear visual map of all 4 clause pathways and their connections."*

---

<!-- SLIDE 5 -->
## Slide 5: Reference Literature - CPOG Theory (Mokhov & Yakovlev 2010)

- **Foundational Paper:**
  - *“Conditional Partial Order Graphs: Model, Synthesis, and Application”*
  - **Authors:** Andrey Mokhov and Alex Yakovlev *(IEEE Transactions on Computers, May 2010)*.
- **Core Principle of CPOG:**
  - Formally defined as a 5-tuple: $H = (V, E, \phi, \rho, S)$.
  - A graph framework that overlays multiple separate operational graphs (called **scenarios** $S$) onto a single shared set of vertices ($V$).
- **How It Works:**
  - Computational units (AND gates, accumulators) form the shared vertices.
  - Boolean conditions ($\rho$) placed on edges activate or deactivate paths depending on an opcode select variable.

> **How to Explain:**  
> *"To address hardware reuse, we studied the foundational 2010 IEEE Transactions on Computers paper by Mokhov and Yakovlev on Conditional Partial Order Graphs. A CPOG mathematically merges multiple separate operational graphs into one shared graph. By placing Boolean conditions on the edges, different pathways are dynamically selected based on an opcode."*

---

<!-- SLIDE 6 -->
## Slide 6: Task 4 - CPOG Synthesis & Hardware Reuse

- **What We Did:**
  - Mapped our 4 Tsetlin clauses into 4 operational scenarios:
    - Mode `00` $\implies C_1^+$, Mode `01` $\implies C_2^+$, Mode `10` $\implies C_1^-$, Mode `11` $\implies C_2^-$
- **How It Enables Hardware Reuse:**
  - **Conventional Approach:** Instantiates 4 separate physical AND evaluation circuits.
  - **With CPOG:** Reuses **1 single shared physical AND unit** to evaluate all 4 clauses sequentially over 4 steps.
- **Minimal Control Routing:**
  - Port 1 selects $x_1$ vs $\bar{x}_1$ using select bit $s_0$.
  - Port 2 selects $x_2$ vs $\bar{x}_2$ using the condition $s_1 \oplus s_0$ (only 1 XOR gate needed).
  - Confirms that resource sharing can be done with negligible switching logic.

> **How to Explain:**  
> *"Here is how CPOG enables hardware reuse. Instead of instantiating 4 separate AND circuits, we reuse 1 physical AND unit to evaluate the 4 clauses one by one. By deriving the Boolean conditions, we found that routing the inputs requires only a single XOR gate, meaning the hardware reuse does not incur heavy control overhead."*

---

<!-- SLIDE 7 -->
## Slide 7: Task 5 - Modeling and Visualizing in Workcraft

- **Integration with Workcraft (Newcastle University):**
  - Workcraft is an open-source EDA framework specifically designed for CPOG modeling and graph-based hardware design ([workcraft.org](https://workcraft.org)).
- **What We Implemented:**
  - Generated native Workcraft project models containing node coordinates, ports, and visual groupings.
  - Formatted models for Workcraft's dedicated CPOG plugin.
- **Visual Inspection in Workcraft:**
  - **Graph Canvas:** Displays vertices, shared connections, and derived Boolean condition labels.
  - **Interactive Scenarios Panel:** Allows selecting each clause scenario (`C1_pos`, `C2_pos`, `C1_neg`, `C2_neg`) to visually highlight active edges and active execution paths.

> 🖼️ **Visual for this Slide:**  
> Screenshot of the **Workcraft GUI** (with `generated/workcraft_cpog.work` open, showing the visual canvas and the right-hand Scenarios Panel).

> **How to Explain:**  
> *"We also integrated our model into Workcraft, an EDA tool developed at Newcastle University for CPOG design. As shown in this screenshot, when you open the model in the GUI, you can visually inspect the graph, see the condition labels, and click through the scenario panel to see which paths are active for each clause."*

---

<!-- SLIDE 8 -->
## Slide 8: Task 6 - Verifying the CPOG Against the IR

- **What We Did:**
  - Evaluated all possible input combinations: `[0,0]`, `[0,1]`, `[1,0]`, and `[1,1]`.
  - Step-by-step validation across three levels:
    1. **Reference Model:** Ground truth output from the initial Tsetlin Machine.
    2. **Compiler IR:** Functional evaluation through the MLIR SSA dataflow graph.
    3. **CPOG Model:** Projection and evaluation of each scenario graph ($H|_S$).
- **Observation:**
  - Every scenario projection in the CPOG matched the corresponding clause evaluation in the MLIR graph across all cases.
  - Confirms that sharing the execution core preserves the exact intended logic behavior.

---
# Thank You!
### Questions & Discussion

> **How to Explain:**  
> *"Finally, we verified the CPOG against the MLIR dataflow graph and reference model by testing all input combinations. Each scenario in the CPOG produced the exact same output as the corresponding clause in the MLIR graph. This confirms that our shared hardware model preserves the correct logic behavior. Thank you, and I am happy to take any questions."*
