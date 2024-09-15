module Matching (
    input [1:0] A0, A1, A2, A3, // 匹配组的4个2位输入
    input [1:0] B0, B1, B2, B3, // 目标组的4个2位输入
    output reg [1:0] out0, out1, out2, out3 // 输出映射
);

    // 占用标记：记录目标组元素是否已经被匹配
    reg used [3:0];
    
    // 临时变量，用来存储当前找到的匹配
    integer i;
    
    // 比较并生成输出
    always @(*) begin
        // 初始化占用标记为0（表示未被使用）
        used[0] = 0;
        used[1] = 0;
        used[2] = 0;
        used[3] = 0;
        
        // 处理 A0 匹配
        for (i = 0; i < 4; i = i + 1) begin
            if (A0 == B0 && !used[0]) begin
                out0 = 2'b00;
                used[0] = 1;
            end
            else if (A0 == B1 && !used[1]) begin
                out0 = 2'b01;
                used[1] = 1;
            end
            else if (A0 == B2 && !used[2]) begin
                out0 = 2'b10;
                used[2] = 1;
            end
            else if (A0 == B3 && !used[3]) begin
                out0 = 2'b11;
                used[3] = 1;
            end
        end

        // 处理 A1 匹配
        for (i = 0; i < 4; i = i + 1) begin
            if (A1 == B0 && !used[0]) begin
                out1 = 2'b00;
                used[0] = 1;
            end
            else if (A1 == B1 && !used[1]) begin
                out1 = 2'b01;
                used[1] = 1;
            end
            else if (A1 == B2 && !used[2]) begin
                out1 = 2'b10;
                used[2] = 1;
            end
            else if (A1 == B3 && !used[3]) begin
                out1 = 2'b11;
                used[3] = 1;
            end
        end

        // 处理 A2 匹配
        for (i = 0; i < 4; i = i + 1) begin
            if (A2 == B0 && !used[0]) begin
                out2 = 2'b00;
                used[0] = 1;
            end
            else if (A2 == B1 && !used[1]) begin
                out2 = 2'b01;
                used[1] = 1;
            end
            else if (A2 == B2 && !used[2]) begin
                out2 = 2'b10;
                used[2] = 1;
            end
            else if (A2 == B3 && !used[3]) begin
                out2 = 2'b11;
                used[3] = 1;
            end
        end

        // 处理 A3 匹配
        for (i = 0; i < 4; i = i + 1) begin
            if (A3 == B0 && !used[0]) begin
                out3 = 2'b00;
                used[0] = 1;
            end
            else if (A3 == B1 && !used[1]) begin
                out3 = 2'b01;
                used[1] = 1;
            end
            else if (A3 == B2 && !used[2]) begin
                out3 = 2'b10;
                used[2] = 1;
            end
            else if (A3 == B3 && !used[3]) begin
                out3 = 2'b11;
                used[3] = 1;
            end
        end
    end
endmodule
