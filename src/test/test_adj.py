#! /usr/bin/env python3

from src.adjacency import *
import numpy as np
import pytest

def test_adjacency():
    nodes = [0, 1, 2, 3, 4, 5]
    edges = {(0, 1): [[0, 0, 0], [1, 0, 0], [-1, 0, 0]], (1, 5): [[0, 0, 0]], (3, 4): [[0, 0, 0], [0, 0, 3]]}
    expected_adj = np.array([
        [0, 3, 0, 0, 0, 0],
        [3, 0, 0, 0, 0, 1],
        [0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 2, 0],
        [0, 0, 0, 2, 0, 0],
        [0, 1, 0, 0, 0, 0]
    ])
    adj = adjacency(nodes, edges)
    assert np.allclose(adj, expected_adj)
    edges = {(0, 1): [[0, 0, 0], [1, 0, 0]], (1, 2): [[-1, 0, 0]], (2, 3): [[-1, 0, 0]], (0, 2): [[0, 1, 0]], (0, 3): [[0, 0, 0]], (4, 5): [[0, 0, 0]]}
    expected_adj = np.array([
        [0, 2, 1, 1, 0, 0],
        [2, 0, 1, 0, 0, 0],
        [1, 1, 0, 1, 0, 0],
        [1, 0, 1, 0, 0, 0],
        [0, 0, 0, 0, 0, 1],
        [0, 0, 0, 0, 1, 0]
    ])
    adj = adjacency(nodes, edges)
    assert np.allclose(adj, expected_adj)
    edges = {(0, 1): [[0, 0, 0], [1, 0, 0]], (1, 2): [[-1, 0, 0]], (2, 3): [[-1, 0, 0]], (0, 2): [[0, 1, 0]], (0, 3): [[0, 0, 0]], (1, 5): [[0, 0, 0]]}
    expected_adj = np.array([
        [0, 2, 1, 1, 0, 0],
        [2, 0, 1, 0, 0, 1],
        [1, 1, 0, 1, 0, 0],
        [1, 0, 1, 0, 0, 0],
        [0, 0, 0, 0, 0, 0],
        [0, 1, 0, 0, 0, 0]
    ])
    adj = adjacency(nodes, edges)
    assert np.allclose(adj, expected_adj)


