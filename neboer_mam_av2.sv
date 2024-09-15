module Matcher (
    input [1:0] A, B0, B1, B2, B3,
    input [3:0] used,
    output reg [1:0] match,
    output reg [3:0] used_out
);
    always @(*) begin
        if (A == B0 && !used[0]) begin match = 2'b00; used_out = used | 4'b0001; end
        else if (A == B1 && !used[1]) begin match = 2'b01; used_out = used | 4'b0010; end
        else if (A == B2 && !used[2]) begin match = 2'b10; used_out = used | 4'b0100; end
        else if (A == B3 && !used[3]) begin match = 2'b11; used_out = used | 4'b1000; end
        else begin match = 2'b00; used_out = used; end
    end
endmodule

module Matching (
    input [1:0] A0, A1, A2, A3,
    input [1:0] B0, B1, B2, B3,
    output [1:0] out0, out1, out2, out3
);
    wire [3:0] used0, used1, used2, used3;

    Matcher m0 (.A(A0), .B0(B0), .B1(B1), .B2(B2), .B3(B3), .used(4'b0000), .match(out0), .used_out(used0));
    Matcher m1 (.A(A1), .B0(B0), .B1(B1), .B2(B2), .B3(B3), .used(used0), .match(out1), .used_out(used1));
    Matcher m2 (.A(A2), .B0(B0), .B1(B1), .B2(B2), .B3(B3), .used(used1), .match(out2), .used_out(used2));
    Matcher m3 (.A(A3), .B0(B0), .B1(B1), .B2(B2), .B3(B3), .used(used2), .match(out3), .used_out(used3));
endmodule
