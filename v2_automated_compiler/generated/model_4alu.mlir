// ==========================================================================
// V2 Automated MLIR Representation for IRIS
// Hardware Constraints: MAX_ALUS = 4
// Schedule: 4 Parallel Cores over 3 Cycles
// Logic Optimization (C+ to deduce C-): Disabled
// ==========================================================================
module {
  func.func @tsetlin_machine_iris(%x1: i1, %x2: i1, %x3: i1, %x4: i1, %x5: i1, %x6: i1, %x7: i1, %x8: i1) -> i1 {
    // --- Literals ---
    %c1_i1 = arith.constant 1 : i1
    %not_x1 = arith.xori %x1, %c1_i1 : i1
    %not_x2 = arith.xori %x2, %c1_i1 : i1
    %not_x3 = arith.xori %x3, %c1_i1 : i1
    %not_x4 = arith.xori %x4, %c1_i1 : i1
    %not_x5 = arith.xori %x5, %c1_i1 : i1
    %not_x6 = arith.xori %x6, %c1_i1 : i1
    %not_x7 = arith.xori %x7, %c1_i1 : i1
    %not_x8 = arith.xori %x8, %c1_i1 : i1

    // --- Loop-Tiled (Folded) Execution: Tiled by 4 ---
    scf.for %step = %c0 to %c3 step %c1 {
      %core0_out = tm.eval_core_lane(%step, 0)
      %core1_out = tm.eval_core_lane(%step, 1)
      %core2_out = tm.eval_core_lane(%step, 2)
      %core3_out = tm.eval_core_lane(%step, 3)
    }
    // --- Voting & Accumulation ---
    %final_decision = tm.accumulate_and_threshold(...)
    return %final_decision : i1
  }
}