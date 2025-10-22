#! /usr/bin/env python3

from src.tree import *
from src.adjacency import *
import pytest



def test_tree():
    isoval = 1.0
    edges = {(0, 1): [[0, 0, 0], [1, 0, 0]], (1, 2): [[-1, 0, 0]], (2, 3): [[-1, 0, 0]], (0, 2): [[0, 1, 0]], (0, 3): [[0, 0, 0]], (4, 5): [[0, 0, 0]]}
    nodes = [0, 1, 2, 3, 4, 5]
    translations, rank = tree(nodes, edges, isoval)
    assert rank == 2
    assert [1, 0, 0] in [list(el) for el in translations]
    assert [-1, 0, 0] in [list(el) for el in translations]
    assert [1, 1, 0] in [list(el) for el in translations]
    assert [1, -1, 0] in [list(el) for el in translations]
    assert [0, 1, 0] in [list(el) for el in translations]
    edges = {(0, 1): [[0, 0, 0], [0, 0, 1]], (1, 2): [[-1, 0, 0]], (2, 3): [[-1, 0, 0]], (0, 2): [[0, 1, 0]], (0, 3): [[0, 0, 0]], (4, 5): [[0, 0, 0]]}
    translations, rank = tree(nodes, edges, isoval)
    assert rank == 3
    edges = {(0, 1): [[0, 0, 0]], (0, 4): [[0, 1, 0]], (1, 3): [[0, 0, 0]], (2, 3): [[-1, 0, 0], [0, 0, 0]], (3, 4): [[1, 0, 0], [0, -1, 1]]}
    translations, rank = tree(nodes, edges, isoval)
    assert rank == 3
    assert [1, -1, 0] in [list(el) for el in translations]
    assert [0, -2, 1] in [list(el) for el in translations]
    assert len(translations) == 3
