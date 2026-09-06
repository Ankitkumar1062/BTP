// ==========================================================================
// MLIR Representation for Tsetlin Machine (XOR Benchmark)
// Dialects: func, arith
// Compiled from Canonical Tsetlin Machine Model
// ==========================================================================
module {
  func.func @tsetlin_machine_xor(%x1: i1, %x2: i1) -> i1 {
    // ------------------------------------------------------------------------
    // Stage 0: Literal Generation (Primary Inputs & Inverters)
    // ------------------------------------------------------------------------
    %c1_i1 = arith.constant 1 : i1
    %not_x1 = arith.xori %x1, %c1_i1 : i1
    %not_x2 = arith.xori %x2, %c1_i1 : i1

    // ------------------------------------------------------------------------
    // Stage 1: Clause Conjunction Trees (Bitwise AND Reductions)
    // ------------------------------------------------------------------------
    %c1_pos = arith.andi %x1, %not_x2 : i1
    %c2_pos = arith.andi %not_x1, %x2 : i1
    %c1_neg = arith.andi %x1, %x2 : i1
    %c2_neg = arith.andi %not_x1, %not_x2 : i1

    // ------------------------------------------------------------------------
    // Stage 2: Voting & Accumulation Tree
    // ------------------------------------------------------------------------
    %c1_pos_ext = arith.extui %c1_pos : i1 to i32
    %c2_pos_ext = arith.extui %c2_pos : i1 to i32
    %c1_neg_ext = arith.extui %c1_neg : i1 to i32
    %c2_neg_ext = arith.extui %c2_neg : i1 to i32
    %pos_votes = arith.addi %c1_pos_ext, %c2_pos_ext : i32
    %neg_votes = arith.addi %c1_neg_ext, %c2_neg_ext : i32

    // ------------------------------------------------------------------------
    // Stage 3: Decision Subtraction & Threshold Comparator
    // ------------------------------------------------------------------------
    %diff = arith.subi %pos_votes, %neg_votes : i32
    %c0_i32 = arith.constant 0 : i32
    %decision = arith.cmpi sge, %diff, %c0_i32 : i32

    return %decision : i1
  }
}