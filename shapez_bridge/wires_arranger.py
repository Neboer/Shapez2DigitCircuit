# 给定空间中的几个点，指定他们之间的连接方法，使用给定的元件在格子上连接这些点。
# 算法：从其中一个点出发，去连接另外一个点。
# 1. A*搜索，允许直接掠过直线，确认掠过直线后需要将直线记为桥。
# 2. 关于起点的选择：

# 判断一个连接是否合法：
# 对于给定的点，有且仅有有连接的点可以互相抵达，无法连接的点无法抵达。
# 如果给定的点已经发出连线，则将下一个可以多伸出一个半线的导线伸一个半线，然后重复上面的步骤。
# 如果连线上所有的点都不可，则退回到上个方案。

from collections import deque

from shapez_map import (
    ElementType,
    Map,
    MapElement,
    WirePath,
    WireFace,
    wireface_from_vector,
    wireface_to_vector
)
from blueprint_code import get_shapez_code_from_blueprint_entries
from blueprint_display import print_blueprint


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


# 在一个map中，找到两点之间所有可能的连接。
# 本质上，是找到start_point的start_face到end_point的end_face的所有可能的连接。
# 注意对应关系，start_point的start_face是连接的起点，end_point的end_face是连接的终点。
# 实际的路径中，start_point和end_point都不在路径中，这符合直觉：导线不会延伸进元件内部。
def wire_2_points(
    start_point: tuple,
    start_face: WireFace,
    end_point: tuple,
    end_face: WireFace,
    init_map: Map,
):

    directions = [WireFace.N, WireFace.E, WireFace.S, WireFace.W]
    path_start_point = (
        start_point[0] + wireface_to_vector(start_face)[0],
        start_point[1] + wireface_to_vector(start_face)[1],
    )
    path_end_point = (
        end_point[0] + wireface_to_vector(end_face)[0],
        end_point[1] + wireface_to_vector(end_face)[1],
    )
    queue = deque(
        [(WirePath([path_start_point], start_face.opposite()), init_map.copy())]
    )

    while queue:
        wire_path, map = queue.popleft()

        if wire_path.path[-1] == path_end_point:
            # 抵达了终点前的最后一个点，现在需要给这个点分配一个形状，以结束此线路的构建并返回线路对地图造成的影响。
            new_wirepath = wire_path.copy()
            new_map = map.copy()
            # 如果这个路径最终抵达终点，那么返回这个确定的路径，返回之前需要将路径的结尾与实际需要的Face对应。
            new_wirepath.end_face = end_face
            last_block_input_wireface = (
                wire_path.start_face
                if len(wire_path.path) == 1
                else wireface_from_vector(wire_path.path[-1], wire_path.path[-2])
            )
            new_map.set_element(
                path_end_point[0],
                path_end_point[1],
                MapElement.from_wirefaces(
                    last_block_input_wireface, end_face.opposite()
                ),
            )

            yield new_wirepath, new_map

        # 没有抵达终点，开始BFS.
        for d in directions:
            new_wirepath = wire_path.copy()
            new_map = map.copy()
            if new_wirepath.extend(d, new_map):
                if wire_map_from_path(new_wirepath, new_map):
                    queue.append((new_wirepath, new_map))


if __name__ == "__main__":
    map = Map(3, 3)
    map.set_element(0, 0, MapElement(ElementType.BLOCKING))
    map.set_element(2, 2, MapElement(ElementType.BLOCKING))
    for path, map in wire_2_points((0, 0), WireFace.S, (2, 2), WireFace.N, map):
        code = get_shapez_code_from_blueprint_entries(map.to_shapez_entries())
        print(code)
