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

    is_wire = lambda x: x in [
        ElementType.IWire,
        ElementType.TWire,
        ElementType.LWire,
        ElementType.CrossWire,
        ElementType.BridgeWire,
    ]


element_type_to_entry_type = {
    ElementType.IWire: "WireDefaultForwardInternalVariant",
    ElementType.TWire: "WireDefaultJunctionInternalVariant",
    ElementType.LWire: "WireDefaultLeftInternalVariant",
    ElementType.CrossWire: "WireDefaultCrossInternalVariant",
    ElementType.BridgeWire: "WireDefaultBridgeInternalVariant",
}


class WireFace(IntEnum):
    N = 0
    E = 1
    S = 2
    W = 3

    def opposite(self):
        return WireFace((self.value + 2) % 4)


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


def wireface_to_vector(face: WireFace):
    if face == WireFace.N:
        return (0, -1)
    elif face == WireFace.E:
        return (1, 0)
    elif face == WireFace.S:
        return (0, 1)
    elif face == WireFace.W:
        return (-1, 0)


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

    def to_shapez_entry(self, x, y):
        return {
            "X": x,
            "Y": y,
            "R": self.rotation,
            "T": element_type_to_entry_type[self.type],
        }


class Map:
    def __init__(self, width, height, init_elements=None):
        self.width = width
        self.height = height
        self.elements = {} if not init_elements else init_elements

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

    def to_shapez_entries(self):
        return [
            e.to_shapez_entry(e_pos[0], e_pos[1])
            for e_pos, e in self.elements.items()
            if e.type.is_wire()
        ]

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
        new_start_face = wireface_from_vector(self.path[-n], self.path[-(n + 1)])
        return WirePath(new_path, new_start_face, self.end_face)

    def extend(self, direction: WireFace, map: Map) -> bool:
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
        if 0 <= new_end[0] < map.width and 0 <= new_end[1] < map.height:
            # 新点在地图内，要延伸的新点是空地或者IWire，并且不与自己相交才能延伸，否则此方向被堵住。
            if (
                map.get_element(new_end[0], new_end[1]).type
                in (
                    ElementType.EMPTY,
                    ElementType.IWire,
                )
                and new_end not in self.path
            ):
                self.path.append(new_end)
                return True

        return False

    def copy(self):
        return copy.deepcopy(self)
