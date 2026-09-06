/*
 * tsetlin_machine.c
 * =================
 * Canonical C implementation of a simple Tsetlin Machine (XOR & MUX Benchmarks).
 * Demonstrates:
 * 1. Literal extraction (x1, ~x1, x2, ~x2)
 * 2. Clause evaluations via bitwise conjunctions (AND reductions)
 * 3. Integer voting and threshold comparison
 *
 * Can be compiled with GCC:
 *   gcc tsetlin_machine.c -o tsetlin_machine.exe
 * Or compiled to MLIR via Polygeist:
 *   cgeist tsetlin_machine.c -function=tsetlin_machine_xor -S
 */

#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>

// Structure representing the trained Tsetlin Machine
typedef struct {
    int num_inputs;
    int num_clauses;
    int clause_polarities[4]; // +1 or -1
} TsetlinMachine;

/*
 * Canonical 2-input XOR Tsetlin Machine:
 * - C1+ (j=0, pol=+1): x1 & ~x2  (detects [1, 0])
 * - C2+ (j=1, pol=+1): ~x1 & x2  (detects [0, 1])
 * - C1- (j=2, pol=-1): x1 & x2   (detects [1, 1])
 * - C2- (j=3, pol=-1): ~x1 & ~x2 (detects [0, 0])
 */
int tsetlin_machine_xor(int x1, int x2) {
    // Stage 0: Literal Inversion
    int not_x1 = 1 - x1;
    int not_x2 = 1 - x2;

    // Stage 1: Clause Conjunctions
    int c1_pos = x1 & not_x2;
    int c2_pos = not_x1 & x2;
    int c1_neg = x1 & x2;
    int c2_neg = not_x1 & not_x2;

    // Stage 2: Voting Adder Tree
    int pos_votes = c1_pos + c2_pos;
    int neg_votes = c1_neg + c2_neg;

    // Stage 3: Threshold Decision (diff >= 0)
    int diff = pos_votes - neg_votes;
    int decision = (diff >= 0) ? 1 : 0;

    return decision;
}

/*
 * Canonical 3-input Multiplexer Tsetlin Machine:
 * Inputs: s (select), a, b
 * - C1+: s & a
 * - C2+: ~s & b
 * - C1-: s & ~a
 * - C2-: ~s & ~b
 */
int tsetlin_machine_mux(int s, int a, int b) {
    int not_s = 1 - s;
    int not_a = 1 - a;
    int not_b = 1 - b;

    int c1_pos = s & a;
    int c2_pos = not_s & b;
    int c1_neg = s & not_a;
    int c2_neg = not_s & not_b;

    int pos_votes = c1_pos + c2_pos;
    int neg_votes = c1_neg + c2_neg;

    int diff = pos_votes - neg_votes;
    return (diff >= 0) ? 1 : 0;
}

int main() {
    printf("===============================================================\n");
    printf("     CANONICAL TSETLIN MACHINE C EXECUTION & VERIFICATION      \n");
    printf("===============================================================\n\n");

    printf("[1] 2-input XOR Benchmark Truth Table:\n");
    printf("  x1 | x2 | Expected | Predicted | Status\n");
    printf("  ---------------------------------------\n");
    int xor_inputs[4][2] = {{0,0}, {0,1}, {1,0}, {1,1}};
    for (int i = 0; i < 4; i++) {
        int x1 = xor_inputs[i][0];
        int x2 = xor_inputs[i][1];
        int expected = x1 ^ x2;
        int pred = tsetlin_machine_xor(x1, x2);
        printf("   %d |  %d |    %d     |     %d     | %s\n", 
               x1, x2, expected, pred, (expected == pred) ? "PASSED" : "FAILED");
    }

    printf("\n[2] 3-input Multiplexer Benchmark Truth Table:\n");
    printf("  s | a | b | Expected | Predicted | Status\n");
    printf("  ---------------------------------------\n");
    for (int s = 0; s <= 1; s++) {
        for (int a = 0; a <= 1; a++) {
            for (int b = 0; b <= 1; b++) {
                int expected = s ? a : b;
                int pred = tsetlin_machine_mux(s, a, b);
                printf("  %d | %d | %d |    %d     |     %d     | %s\n", 
                       s, a, b, expected, pred, (expected == pred) ? "PASSED" : "FAILED");
            }
        }
    }

    printf("\nC Implementation Execution Completed Successfully.\n");
    return 0;
}
