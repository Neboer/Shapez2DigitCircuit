 # 蓝图编码规范

 坐标系：

 1. 所有坐标都是从左上开始计算的，以N正向上为基准，X为横向，Y为纵向。
 
 1. 所有形状分为2旋转和4旋转。
    2旋转时，旋转分别为1,2；
    4旋转时，旋转分别为0,1,2,3；
    4旋转时，顺时针旋转可以让旋转变大。

 
 ## 所有形状
 

| 名字| 正方向示意| 总旋转   |
| --------| -------| ------- |
| WireDefaultForwardInternalVariant  | ![](./shapes/wires/WireDefaultForwardInternalVariant.svg)| 2 |
| WireDefaultJunctionInternalVariant  | ![](./shapes/wires/WireDefaultJunctionInternalVariant.svg)| 4 |
| WireDefaultLeftInternalVariant  | ![](./shapes/wires/WireDefaultLeftInternalVariant.svg)| 4 |
| WireDefaultCrossInternalVariant  | ![](./shapes/wires/WireDefaultCrossInternalVariant.svg)| 1 |
| WireDefaultBridgeInternalVariant  | ![](./shapes/wires/WireDefaultBridgeInternalVariant.svg)| 2 |
