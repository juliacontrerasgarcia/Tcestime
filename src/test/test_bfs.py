#! /usr/bin/env python3

from src.tree import *
from src.adjacency import *
import pytest




def test_tree():
    edges = {(0, 1): [[0, 0, 0], [1, 0, 0]], (1, 2): [[-1, 0, 0]], (2, 3): [[-1, 0, 0]], (0, 2): [[0, 1, 0]], (0, 3): [[0, 0, 0]], (4, 5): [[0, 0, 0]]}
    nodes = [0, 1, 2, 3, 4, 5]
    adj = adjacency(nodes, edges)
    conn_nodes, paths, gens, count = my_bfs(0, adj, nodes, edges)
    assert conn_nodes == [0, 1, 2, 3]
    assert len(gens) == 3
    assert [0, 1, 0] in paths
    assert [0, 1, 2] in paths
    assert [0, 2, 3] in paths
    assert [0, 3] in paths
    assert count[0] == 2
    assert count[1] == 1
    assert count[2] == 2
    assert count[3] == 2

    conn_nodes, paths, gens, count = my_bfs(1, adj, nodes, edges)
    assert all([n in conn_nodes for n in [0,1,2,3]])
    assert len(gens) == 3
    assert [1, 0, 1] in paths
    assert [1, 0, 2] in paths
    assert [1, 0, 3] in paths
    assert [1, 2,  3] in paths
    assert count[0] == 1
    assert count[1] == 2
    assert count[2] == 2
    assert count[3] == 2

    conn_nodes, paths, gens, count = my_bfs(4, adj, nodes, edges)
    assert all([n in conn_nodes for n in [4, 5]])
    assert len(gens) == 2
    assert len(paths) == 1
    assert [4, 5] in paths
    assert count[4] == 1 
    assert count[5] == 1
