#! /usr/bin/env python


import numpy as np


def my_bfs(source, adj, nodes, edges):
    adj_temp = np.copy(adj)
    seen = []
    nextlevel = [source]
    all_paths = [[nextlevel]]
    all_gens = []
    count = {}
    gen = 0
    while nextlevel:
        all_paths.append([])
        thislevel = nextlevel
        nextlevel = []
        # v is the node on thislevel, whose children I will look for (u)
        added = []
        for v in thislevel:
            if v in seen:
                count[v] += 1
            if v not in seen:
                seen.append(v)
                count[v] = 1
                for u in np.where(adj_temp[v])[0]:
                    nextlevel.append(u)
                    # Register that this connection has been counted already
                    adj_temp[v, u] -= 1
                    adj_temp[u, v] -= 1
                    for old_path in all_paths[gen]:
                        if old_path[-1] == v:
                            all_paths[-1].append(old_path + [u])
                            added.append(old_path)
                    
        for old_path in all_paths[gen]:
            if old_path not in added:
                all_paths[-1].append(old_path)
                
        gen += 1
        all_gens.append(thislevel)

    return [nodes[i] for i in seen], [[nodes[i] for i in path] for path in all_paths[-1]], [[ nodes[i] for i in gen] for gen in all_gens], dict([(nodes[i], count[i]) for i in count.keys()])

