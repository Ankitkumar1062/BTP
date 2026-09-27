// ==========================================================================
// V2 Automated MLIR Representation for XOR
// Hardware Constraints: MAX_ALUS = 2
// Schedule: 2 Parallel Cores over 1 Cycles
// Logic Optimization (C+ to deduce C-): Enabled
// ==========================================================================
module {
  func.func @tsetlin_machine_xor(%x1: i1, %x2: i1) -> i1 {
    // --- Literals ---
    %c1_i1 = arith.constant 1 : i1
    %not_x1 = arith.xori %x1, %c1_i1 : i1
    %not_x2 = arith.xori %x2, %c1_i1 : i1

    // --- Fully Unrolled (Parallel) Execution ---
    %c1_pos = tm.eval_clause(%x1, %not_x2)
    %c2_pos = tm.eval_clause(%not_x1, %x2)
    // --- Voting & Accumulation ---
    %final_decision = tm.accumulate_and_threshold(...)
    return %final_decision : i1
  }
}