# yosys2shapez

将yosys综合system verilog语言得到的json代码转换成shapez2中对应的逻辑电路。

## 通用数据结构

为了方便在shapez2中交换数据，定义一个数据结构来描述shapez2-yosys。它可以轻易的被序列化，也可以被读取解析成特定的数据结构。


## 转换规则：

1. 拆位

    shapez2中，每条导线可以表达形状、多位数和布尔值，但是shapez2中并没有提供针对这种特殊导线的加法器、位运算器，因此我们无法轻易对导线进行拆位和解位。

    因此，对于在传输过程中涉及到总线操作(BusSlice, BusGroup)的导线，需要拆位打开，同时将对应的目标机器直接连接到位的发出方上。

2. 布局

    对于拆好的每个元件device，找到其在shapez2中对应的机器。
    这里需要一个预构建的过程：程序输出还缺少什么类型的机器，让人去在shapez2中完成设计，然后再把机器的代码粘贴上。

    元件是shapez2中的蓝图，记录在程序中。

    元件类型一共有如下几种：

    |type|input_bits|output_bits|
    |---|---|---|
    |Not|1|1|
    |BusGroup|  |  |
    |And|  |  |
    |Constant|  |  |
    |Mux|  |  |
    |Output|  |  |
    |BusSlice|  |  |
    |Or|  |  |
    |Input|  |  |
    |Eq|  |  |