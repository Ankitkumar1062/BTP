// ==========================================================================
// V2 Automated MLIR Representation for XOR
// Hardware Constraints: MAX_ALUS = 1
// Schedule: 1 Parallel Cores over 2 Cycles
// Logic Optimization (C+ to deduce C-): Enabled
// ==========================================================================
module {
  func.func @tsetlin_machine_xor(%x1: i1, %x2: i1) -> i1 {
    // --- Literals ---
    %c1_i1 = arith.constant 1 : i1
    %not_x1 = arith.xori %x1, %c1_i1 : i1
    %not_x2 = arith.xori %x2, %c1_i1 : i1

    // --- Loop-Tiled (Folded) Execution: Tiled by 1 ---
    scf.for %step = %c0 to %c2 step %c1 {
      %core0_out = tm.eval_core_lane(%step, 0)
    }
    // --- Voting & Accumulation ---
    %final_decision = tm.accumulate_and_threshold(...)
    return %final_decision : i1
  }
}