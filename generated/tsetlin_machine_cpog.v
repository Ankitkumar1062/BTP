// =============================================================================
// Module: tsetlin_machine_cpog
// Description: Synthesizable Verilog RTL for CPOG-Synthesized Tsetlin Machine
// Benchmark: XOR (2-input XOR, 4 Clauses)
// Hardware: 1 Shared AND Core, 2 Single-Gate MUXes, 1 Signed Accumulator
// =============================================================================

module tsetlin_machine_cpog (
    input  wire        clk,
    input  wire        rst_n,
    input  wire        start,
    input  wire [1:0]  x_in,          // Primary inputs: [x1, x2]
    output reg         done,
    output reg         class_out,     // Final predicted class (0 or 1)
    output reg  signed [4:0] vote_sum // Accumulated vote tally
);

    // -------------------------------------------------------------------------
    // 1. Literal Generation (Stage 0)
    // -------------------------------------------------------------------------
    wire x1     = x_in[0];
    wire x2     = x_in[1];
    wire not_x1 = ~x1;
    wire not_x2 = ~x2;

    // -------------------------------------------------------------------------
    // 2. CPOG Scenario Sequencer (s1, s0)
    // Scenario 00: C1+ (x1 & ~x2)  -> +1
    // Scenario 01: C2+ (~x1 & x2)  -> +1
    // Scenario 10: C1- (x1 & x2)   -> -1
    // Scenario 11: C2- (~x1 & ~x2) -> -1
    // -------------------------------------------------------------------------
    reg [1:0] state;
    reg [1:0] scenario; // [s1, s0]
    
    localparam IDLE    = 2'b00;
    localparam EVAL    = 2'b01;
    localparam FINISH  = 2'b10;

    wire s1 = scenario[1];
    wire s0 = scenario[0];

    // -------------------------------------------------------------------------
    // 3. Synthesized CPOG Boolean Multiplexer Select Controls (rho)
    // MUX 1 Select: sel_mux1 = s0  (0 -> x1, 1 -> ~x1)
    // MUX 2 Select: sel_mux2 = ~(s1 ^ s0) (0 -> x2, 1 -> ~x2)
    // -------------------------------------------------------------------------
    wire sel_mux1 = s0;
    wire sel_mux2 = ~(s1 ^ s0);

    wire lit1 = sel_mux1 ? not_x1 : x1;
    wire lit2 = sel_mux2 ? not_x2 : x2;

    // -------------------------------------------------------------------------
    // 4. Shared 2-input AND Reduction Core (phi = 1)
    // -------------------------------------------------------------------------
    wire clause_active = lit1 & lit2;

    // -------------------------------------------------------------------------
    // 5. Signed Accumulation & Control FSM
    // -------------------------------------------------------------------------
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            state     <= IDLE;
            scenario  <= 2'b00;
            vote_sum  <= 5'sd0;
            class_out <= 1'b0;
            done      <= 1'b0;
        end else begin
            case (state)
                IDLE: begin
                    done     <= 1'b0;
                    scenario <= 2'b00;
                    vote_sum <= 5'sd0;
                    if (start) begin
                        state <= EVAL;
                    end
                end

                EVAL: begin
                    // Accumulate clause vote: +1 if s1==0, -1 if s1==1
                    if (clause_active) begin
                        if (!s1)
                            vote_sum <= vote_sum + 5'sd1;
                        else
                            vote_sum <= vote_sum - 5'sd1;
                    end

                    if (scenario == 2'b11) begin
                        state <= FINISH;
                    end else begin
                        scenario <= scenario + 2'b01;
                    end
                end

                FINISH: begin
                    // Stage 3: Threshold Decision (vote_sum >= 0 -> class 1)
                    class_out <= (vote_sum >= 5'sd0) ? 1'b1 : 1'b0;
                    done      <= 1'b1;
                    state     <= IDLE;
                end

                default: state <= IDLE;
            endcase
        end
    end

endmodule
