#! /usr/bin/env python3

import numpy as np


def adjacency(nodes, edges, verbose=False):
    adjacency = np.zeros((len(nodes), len(nodes))).astype(int)
    for i1, node1 in enumerate(nodes):
        for i2, node2 in enumerate(nodes):
            if (node1, node2) in list(edges.keys()):
                adjacency[i1, i2] += len(edges[(node1, node2)])
                adjacency[i2, i1] += adjacency[i1, i2]
    if verbose:
        print("Adjacency matrix: ")
        print(adjacency)
    return adjacency
