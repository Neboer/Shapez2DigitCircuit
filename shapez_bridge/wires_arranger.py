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
    Map,
    ElementType,
    WireFace,
    MapElement,
    WirePath,
    wire_map_from_path,
    wireface_from_vector,
)
from blueprint_display import print_blueprint

# 在一个map中，找到两点之间所有可能的连接。
def wire_2_points(
    start_point: tuple,
    start_face: WireFace,
    end_point: tuple,
    end_face: WireFace,
    init_map: Map,
):

    directions = [WireFace.N, WireFace.E, WireFace.S, WireFace.W]
    queue = deque([(WirePath([start_point], start_face), init_map.copy())])

    while queue:
        wire_path, map = queue.popleft()

        if wire_path.path[-1] == end_point:
            new_wirepath = wire_path.copy()
            new_map = map.copy()
            # 如果这个路径最终抵达终点，那么返回这个确定的路径，返回之前需要将路径的结尾与实际需要的Face对应。
            new_wirepath.end_face = end_face
            last_block_input_wireface = (
                wire_path.start_face
                if len(wire_path.path) == 1
                else wireface_from_vector(wire_path.path[-2], wire_path.path[-1])
            )
            new_map.set_element(
                end_point[0],
                end_point[1],
                MapElement.from_wirefaces(last_block_input_wireface, end_face),
            )

            yield new_wirepath, new_map

        # 没有抵达终点，开始BFS.
        for d in directions:
            new_wirepath = wire_path.copy()
            new_map = map.copy()
            if new_wirepath.extend(d, new_map.width, new_map.height):
                if wire_map_from_path(new_wirepath, new_map):
                    queue.append((new_wirepath, new_map))

if __name__ == "__main__":
    for path, map in wire_2_points((0, 0), WireFace.S, (2, 2), WireFace.N, Map(3, 3)):
        print(len(path.path))
