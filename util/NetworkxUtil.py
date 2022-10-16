# -*- coding: utf-8 -*-
# python 3.x
# Filename: NetworkxUtil.py
# 定义一个NetworkxUtil工具类实现网状图操作相关的功能

from util.LogUtil import LogUtil
import networkx as nx
import matplotlib.pyplot as plt


class NetworkxUtil:
    @staticmethod
    def shortestPath(G, source=None, target=None, weight=None, method="dijkstra"):
        """
        获取图中两点间的路径
        :param source: 源节点
        :param target: 目标节点
        :param weight: 权重
        :param method: 算法
        :return: 最短路径，不存在返回 []
        """
        try:
            return nx.shortest_path(G, source=source, target=target, weight=weight, method=method)
        except Exception as err:
            LogUtil.e('shortestPath 错误信息：', err)
            return []


# def updatePos(G, pos, nodes, x):
#     pos.update({n: (x, i + 0.5) for i, n in enumerate(nodes)})
#     next_nodes = []
#     for node in nodes:
#         LogUtil.d("node", node, "neighbors", list(G.neighbors(node)))
#         for neighbor in list(G.neighbors(node)):
#             if neighbor not in next_nodes:
#                 next_nodes.append(neighbor)
#     if next_nodes:
#         updatePos(G, pos, next_nodes, x + 1)


if __name__ == "__main__":
    G = nx.DiGraph([(0, 3), (1, 3), (2, 4), (3, 5), (3, 6), (5, 6), (4, 5), (7, 9)])

    options = {
        # "font_size": 36,
        "node_size": 3000,
        "node_color": "white",
        "edgecolors": "black",
        "linewidths": 1,
        "width": 1,
    }

    # group nodes by column
    left_nodes = [0, 1, 2]
    middle_nodes = [3, 4]
    right_nodes = [5, 6]

    # set the position according to column (x-coord)
    pos = {n: (0, i) for i, n in enumerate(left_nodes)}
    pos.update({n: (1, i + 0.5) for i, n in enumerate(middle_nodes)})
    pos.update({n: (2, i + 0.5) for i, n in enumerate(right_nodes)})

    # nx.draw_networkx(G, pos, **options)
    # nx.draw_networkx(G, **options)
    # nx.draw_networkx(G, pos=nx.circular_layout(G))
    # nx.draw_networkx(G, pos=nx.spectral_layout(G))
    # nx.draw_networkx(G, pos=nx.spectral_layout(G))
    # nx.draw_networkx(G, pos=nx.shell_layout(G))
    # nx.draw_networkx(G, pos=nx.planar_layout(G))
    # nx.draw_networkx(G, pos=nx.spiral_layout(G))

    LogUtil.d(nx.shortest_path(G, 1, 5))
    # LogUtil.d(G.number_of_edges(1, 2))
    # LogUtil.d(G.number_of_edges(2, 6))
    # LogUtil.d(G.number_of_edges(6, 2))
    LogUtil.d(G.number_of_nodes())
    for node in G.nodes:
        LogUtil.d("node", node, "in_degree", G.in_degree(node))

    roots = []
    for i, c in enumerate(nx.connected_components(G.to_undirected())):
        print(f"Island {i + 1}: {c}")
        for node in c:
            if G.in_degree(node) == 0:
                roots.append(node)
    LogUtil.d("roots", roots)

    # pos = {n: (0, i) for i, n in enumerate(roots)}
    # pos = {}
    # updatePos(G, pos, roots, 0)
    # nx.draw_networkx(G, pos, **options)
    # LogUtil.d(list(G.neighbors(4)))

    # LogUtil.d(nx.shortest_path(G, 1, 4))
    # Set margins for the axes so that nodes aren't clipped
    ax = plt.gca()
    ax.margins(0.20)
    plt.axis("off")
    plt.show()
    pass
