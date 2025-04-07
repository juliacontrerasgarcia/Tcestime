#! /usr/bin/env python


import numpy as np
from src.bfs import *
from src.adjacency import *


def tree(nodes, edges, translations, at_nums, isoval, dim1, dim2, dim3, anti_phi, verbose=True):
    adj = adjacency(nodes, edges)
    #translations = []
    for i_node, node in enumerate(nodes):
        network_with_H = False  # So we can later check if it has H or not to determine netval
        conn_nodes, paths, gens, count = my_bfs(i_node, adj, nodes, edges)
        if verbose:
            print(" ")
            print(" ")
            print("Node 1 : ", node)
            print("Connected network : ", conn_nodes)
            print("Possible paths : ", paths)
            print("Generations : ", gens)
            print("Node count : ", count)

        idx_conn = []
        for i2, node2 in enumerate(conn_nodes):
            idx_conn.append(np.where(np.array(nodes)==node2)[0])
        idx_conn = np.array(idx_conn).reshape(len(conn_nodes))
        idx_Hs = np.where(np.array(at_nums)[idx_conn]==1.0)[0]
        #print(np.array(at_nums)[idx_conn])
        #print(idx_Hs)
        #print(len(idx_Hs))
        #print(count)
        #print(conn_nodes)
        if len(idx_Hs)>1:
            network_with_H = True
            if anti_phi == 0.0:
                anti_phi = isoval
                print("Molecularity index: ", anti_phi)
        elif len(idx_Hs) == 1 and len(conn_nodes)>1: 
            if count[conn_nodes[idx_Hs[0]]]>1:
                network_with_H = True                
                if anti_phi == 0.0:
                    anti_phi = isoval
                    print("Molecularity index: ", anti_phi)
        
        translations = []
        for i2, node2 in enumerate(conn_nodes):
            # If a node appears more than once I need to find path 
            trans_paths = {}
            if count[node2] > 1:
                translations_node = []
                if verbose:
                    print("")
                    print("Node 2 :", node2)
                for path in paths:
                    if node2 in path[1:]: # I am not interested if node2 is only root node
                        # For each path containing node2, I compute translation up until that node
                        # I am sure this could be done faster
                        if verbose:
                            print("Path: ", path)
                    
                        trans_path = [[0, 0, 0]] # different trans for this node in this path
                        for j in range(len(path)-1):
                            try:
                                if verbose:
                                    print((path[j], path[j+1]), edges[(path[j], path[j+1])])
                                edge_trans = edges[(path[j], path[j+1])]
                                edge = (path[j], path[j+1])
                            except: # in case connection is backwards
                                if verbose:
                                    print((path[j], path[j+1]), [[-1*el for el in lst_trans] for lst_trans in edges[(path[j+1], path[j])]])
                                edge_trans = [[-1*el for el in lst_trans] for lst_trans in edges[(path[j+1], path[j])]]
                                edge = (path[j], path[j+1])
                            # If edge has only one translation, summing is easy
                            if len(edge_trans) == 1:
                                trans_path = [[sum(x) for x in zip(lst_trans, edge_trans[0])] for lst_trans in trans_path]
                            # otherwise we must consider all possibilities
                            else:
                                # Copy all path translations
                                trans_path_new = trans_path[:]
                                for n_trans in edge_trans:
                                    # For each new translation, we have a list of old trans + new trans
                                    n_trans_path = [[sum(x) for x in zip(tp, n_trans)] for tp in trans_path]
                                    # Add them to final list of trans only if it is not already in it
                                    for ntp in n_trans_path:
                                        if ntp not in trans_path_new:
                                            trans_path_new.append(ntp)
                                    trans_path = trans_path_new[:] # Replace old path trans list with new one

                            # Stop when we reach edge in question
                            if edge[-1] == node2:
                                break

                        # Add all new path translations to dict for this branch (node2)
                        for tp in trans_path:
                            if tuple(path) not in trans_paths.keys():
                                trans_paths[tuple(path)] = [tp]
                            else:
                                if tp not in trans_paths[tuple(path)]:
                                    trans_paths[tuple(path)] += [tp]
                                
                # These are all possible path translations for all node2 banches
                if verbose:
                    print("Translation per path", trans_paths)
                
                # Here I sum different path translations to see final translation from node2 to itself        
                for j1, path1 in enumerate(trans_paths.keys()):
                    if path1.count(node2)>1 and path1[0]==node2:
                        translations_node+=trans_paths[path1]
                        translations+=trans_paths[path1]
                    for j2, path2 in enumerate(trans_paths.keys()):
                        if path1!=path2 and j1 > j2:
                            for t1 in trans_paths[path1]:
                                for t2 in trans_paths[path2]:
                                    diff12 = [t1[i]-t2[i] for i in range(3)]
                                    if diff12 not in translations:
                                        translations.append(diff12)
                                        rank = np.linalg.matrix_rank(translations)
                                        if rank >= 1 and dim1 == False: # and network_with_H:
                                            dim1 = True
                                            #if verbose:
                                            print("Found one-dimensional periodic network at isovalue ", isoval)
                                        if rank >= 2 and dim2 == False: # and network_with_H:
                                            dim2 = True
                                            #if verbose:
                                            print("Found two-dimensional periodic network at isovalue ", isoval)
                                        if rank >= 3: # and network_with_H:
                                            if verbose:
                                                #print("Found three-dimensional periodic network at isovalue ", isoval)
                                                print("Total translations: ", translations)
                                            return translations, rank, dim1, dim2, dim3, anti_phi
                                            exit()

    if verbose:
        print("Total translations: ", translations)
    return translations, np.linalg.matrix_rank(translations), dim1, dim2, dim3, anti_phi


