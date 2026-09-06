// ==========================================================================
// High-Level 'tm' Dialect MLIR Representation (XOR)
// ==========================================================================
module {
  func.func @tm_highlevel_xor(%x1: i1, %x2: i1) -> i1 {
    %literals = tm.literal_extract(%x1, %x2) : (i1, i1) -> !tm.literals<4>
    %c1_pos = tm.clause(%literals) {include_mask = [1, 0, 0, 1], polarity = "pos"} : (!tm.literals<4>) -> i1
    %c2_pos = tm.clause(%literals) {include_mask = [0, 1, 1, 0], polarity = "pos"} : (!tm.literals<4>) -> i1
    %c1_neg = tm.clause(%literals) {include_mask = [1, 0, 1, 0], polarity = "neg"} : (!tm.literals<4>) -> i1
    %c2_neg = tm.clause(%literals) {include_mask = [0, 1, 0, 1], polarity = "neg"} : (!tm.literals<4>) -> i1
    %pos_votes = tm.vote_accumulate(%c1_pos, %c2_pos) : i32
    %neg_votes = tm.vote_accumulate(%c1_neg, %c2_neg) : i32
    %decision = tm.threshold(%pos_votes, %neg_votes) : (i32, i32) -> i1
    return %decision : i1
  }
}