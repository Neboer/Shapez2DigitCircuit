# 给我一段路径，给你用这段路径画导线之后更新的地图，如果这段路径不合法，返回None。
# 地图内Element分为两种，
#   所有“本来就不能经过的点”称作 ori_blockings_element，只包含元件内部的点。
#   地图中的所有“导线”都属于 wires_element，这些导线包含其他路径形成的线和当前路径已经形成的线。

import copy
from enum import Enum, IntEnum


class ElementType(Enum):
    EMPTY = 0
    BLOCKING = 1

    IWire = 2
    TWire = 3
    LWire = 4
    CrossWire = 5
    BridgeWire = 6


class WireFace(IntEnum):
    N = 0
    E = 1
    S = 2
    W = 3


face_table = {
    ElementType.IWire: [WireFace.N, WireFace.S],
    ElementType.TWire: [WireFace.N, WireFace.E, WireFace.S],
    ElementType.LWire: [WireFace.N, WireFace.W],
    ElementType.CrossWire: [WireFace.N, WireFace.E, WireFace.S, WireFace.W],
    ElementType.BridgeWire: [WireFace.N, WireFace.E, WireFace.S, WireFace.W],
}


# 向量方向
def wireface_from_vector(point1, point2):
    if point1[0] == point2[0]:
        if point1[1] > point2[1]:
            return WireFace.N
        else:
            return WireFace.S
    else:
        if point1[0] > point2[0]:
            return WireFace.W
        else:
            return WireFace.E


class MapElement:
    def __init__(self, type=ElementType.EMPTY, rotation=0):
        self.type = type
        self.rotation = rotation

    # 提供两个wireface，给出可以连接两个face的元件类型和其旋转。
    @staticmethod
    def from_wirefaces(face1: WireFace, face2: WireFace):
        if abs(face1 - face2) == 2:
            # 是直线，是横的还是竖的？
            if face1 in [WireFace.N, WireFace.S]:
                # 直线的旋转只有1,2两种可能，竖线是1，横线是2。
                return MapElement(type=ElementType.IWire, rotation=1)
            else:
                return MapElement(type=ElementType.IWire, rotation=2)
        elif abs(face1 - face2) == 1:
            # 不是直线，是L型。如何判定旋转？
            # 旋转的判定方法是，取两个face中较小的那个，然后加1，就是旋转的值。
            return MapElement(type=ElementType.LWire, rotation=min(face1, face2) + 1)
        elif abs(face1 - face2) == 3:
            # 一定是W-N对应的L角。
            return MapElement(type=ElementType.LWire, rotation=0)
        else:
            # face1和face2相等，无法找到这样的wireface。
            raise ValueError("Invalid wire faces.")


class Map:
    def __init__(self, width, height, init_elements=None):
        self.width = width
        self.height = height
        self.elements = (
            {} if not init_elements else init_elements
        )  # (x, y) -> MapElement
    
    def guard_xy(self, x, y):
        if x < 0 or x >= self.width or y < 0 or y >= self.height:
            raise ValueError("Out of map range.")

    def get_element(self, x, y) -> MapElement:
        self.guard_xy(x, y)
        if (x, y) in self.elements:
            return self.elements[(x, y)]
        else:
            return MapElement()

    def set_element(self, x, y, map_element: MapElement):
        self.guard_xy(x, y)
        self.elements[(x, y)] = map_element

    def copy(self):
        return copy.deepcopy(self)


class WirePath:
    def __init__(
        self, path: list[tuple], start_face: WireFace, end_face: WireFace | None = None
    ):
        self.path = path
        self.start_face = start_face
        self.end_face = end_face

    def tail(self, n):
        # 取小尾巴
        new_path = self.path[-n:]
        new_start_face = wireface_from_vector(new_path[-(n + 1)], new_path[-n])
        return WirePath(new_path, new_start_face, self.end_face)

    def extend(self, direction: WireFace, map_width, map_height) -> bool:
        # 在路径末尾延伸一个点，这个点必须不与自身相交。
        new_end = self.path[-1]
        if direction == WireFace.N:
            new_end = (new_end[0], new_end[1] - 1)
        elif direction == WireFace.E:
            new_end = (new_end[0] + 1, new_end[1])
        elif direction == WireFace.S:
            new_end = (new_end[0], new_end[1] + 1)
        elif direction == WireFace.W:
            new_end = (new_end[0] - 1, new_end[1])
        if 0 <= new_end[0] < map_width and 0 <= new_end[1] < map_height:
            if new_end not in self.path:
                self.path.append(new_end)
                return True

        return False

    def copy(self):
        return copy.deepcopy(self)


# 终于，从一个路径中更新一个地图，并判断路径是否可以在地图中实现。
def wire_map_from_path(wire_path: WirePath, current_map: Map) -> bool:
    if len(wire_path.path) == 1:
        return True  # 什么也不会改变，因为我们不知道线要走向何方。
    elif len(wire_path.path) == 2:
        # 准备确定第一截路径所在区域应该是什么块，先看看那一截有东西吗？
        current_element0 = current_map.get_element(
            wire_path.path[0][0], wire_path.path[0][1]
        )
        if current_element0.type in (ElementType.EMPTY, ElementType.IWire):
            # 只有空地或者直线的时候，才有可能在这里布线，否则休想。
            # 可以确定第一截路径所在区域应该是什么块了。
            start, end = wire_path.path[0], wire_path.path[1]
            face1 = wireface_from_vector(start, end)
            new_element0 = MapElement.from_wirefaces(wire_path.start_face, face1)
            # 现在看看那里是不是可以布线。
            if current_element0.type == ElementType.EMPTY:
                # 空地，可以直接布线。
                current_map.set_element(
                    wire_path.path[0][0], wire_path.path[0][1], new_element0
                )
                return True
            # 否则，当前的线一定是IWire，或许可以在布线的时候改成BridgeWire，不过这要求这两条线的方向必须不同。
            elif current_element0.rotation != new_element0.rotation:
                current_map.set_element(
                    wire_path.path[0][0],
                    wire_path[0][1],
                    MapElement(ElementType.BridgeWire),
                )
                return True
            else:
                # 无法在两个走向相同的线上布线。
                return False
        else:
            # 路径冲突，无法布线。
            return False
    elif len(wire_path.path) >= 3:
        # 超过3，直接取小尾巴计算地图更新。
        return wire_map_from_path(wire_path.tail(2), current_map)
