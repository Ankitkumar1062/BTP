// =============================================================================
// Testbench: tb_tsetlin_machine_cpog
// Description: Self-checking testbench for CPOG Tsetlin Machine RTL
// =============================================================================

`timescale 1ns / 1ps

module tb_tsetlin_machine_cpog;

    reg        clk;
    reg        rst_n;
    reg        start;
    reg  [1:0] x_in;
    wire       done;
    wire       class_out;
    wire signed [4:0] vote_sum;

    // Instantiate DUT
    tsetlin_machine_cpog dut (
        .clk(clk),
        .rst_n(rst_n),
        .start(start),
        .x_in(x_in),
        .done(done),
        .class_out(class_out),
        .vote_sum(vote_sum)
    );

    // Clock Generation (100 MHz)
    always #5 clk = ~clk;

    // Test Procedure
    reg [1:0] test_vectors [0:3];
    reg       expected_out [0:3];
    integer   i;
    integer   errors;

    initial begin
        // Initialize Vectors (2-input XOR: 00->0, 01->1, 10->1, 11->0)
        test_vectors[0] = 2'b00; expected_out[0] = 1'b0;
        test_vectors[1] = 2'b01; expected_out[1] = 1'b1;
        test_vectors[2] = 2'b10; expected_out[2] = 1'b1;
        test_vectors[3] = 2'b11; expected_out[3] = 1'b0;

        clk    = 0;
        rst_n  = 0;
        start  = 0;
        x_in   = 2'b00;
        errors = 0;

        #20 rst_n = 1;
        #20;

        $display("===============================================================");
        $display("       SIMULATING SYNTHESIZABLE CPOG VERILOG RTL DATAPATH      ");
        $display("===============================================================");

        for (i = 0; i < 4; i = i + 1) begin
            x_in  = test_vectors[i];
            start = 1;
            #10;
            start = 0;

            // Wait for done
            @(posedge done);
            #1;

            if (class_out === expected_out[i]) begin
                $display("  Vector %b | Expected: %b | Actual: %b | Votes: %d [PASSED]", 
                         test_vectors[i], expected_out[i], class_out, vote_sum);
            end else begin
                $display("  Vector %b | Expected: %b | Actual: %b | Votes: %d [FAILED]", 
                         test_vectors[i], expected_out[i], class_out, vote_sum);
                errors = errors + 1;
            end
            #20;
        end

        $display("===============================================================");
        if (errors == 0)
            $display("  ALL TEST VECTORS PASSED - CYCLE-ACCURATE RTL VERIFIED [100%%]");
        else
            $display("  TEST FAILED WITH %d ERRORS", errors);
        $display("===============================================================");

        $finish;
    end

endmodule
