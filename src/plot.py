#! /usr/bin/env python3

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

def plot_connect(fname, positions, tp_labels, ind_labels, connectivity, legend=None):
    if len(positions)!=len(tp_labels):
        raise ValueError("Position and type label arrays should have the same length.")
    if len(positions)!=len(ind_labels):
        raise ValueError("Position and indicator label arrays should have the same length.")
    if len(positions)!=len(connectivity):
        raise ValueError("Connectivity matrix has wrong dimensions.")

    N = len(positions)
    fig = plt.figure(figsize=[16., 12.])
    ax = fig.add_subplot(1, 1, 1, projection="3d")
    colors = ['red', 'blue']
    legend = ['NUC', 'NNA']
    for i_tp in [0, 1]:
        idx_tp = np.where(np.array(tp_labels)==i_tp)
        if i_tp==0:
            ax.scatter(
                positions[idx_tp, 0], positions[idx_tp, 1], positions[idx_tp, 2], color=colors[i_tp], s=200, label=legend[i_tp]
            )
        else:
            ax.scatter(
                positions[idx_tp, 0], positions[idx_tp, 1], positions[idx_tp, 2], color=colors[i_tp], s=50, label=legend[i_tp]
            )

    if legend is not None:
        ax.legend()
    for i in range(N):
        ax.text(positions[i, 0], positions[i, 1], positions[i, 2], str(ind_labels[i]))

    for i in range(N):
        for j in range(i):
            if connectivity[i, j] > 0 and not np.allclose(positions[i], positions[j]):
                plt.plot([positions[i, 0], positions[j, 0]], [positions[i, 1], positions[j, 1]], [positions[i, 2], positions[j, 2]], c='k', lw=0.5)

    plt.savefig(fname)
    plt.close()
    #plt.show()


def plot_uc(nodes, adj, df_all, fn_out):
   
    pos_nodes_crys = []
    types = []
    for node in nodes:
        ind_node = node
        pos_nodes_crys.append(np.array(df_all[df_all["ind_unique"]==ind_node]["position_crys"].values[0]))
        types.append(df_all[df_all["ind_unique"]==ind_node]["type"].values[0])
    pos_nodes_crys = np.array(pos_nodes_crys)
    tp_dict = {"nuc" : 0, "nna" : 1, "b" : 2}
    tp_labels=list(map(lambda x: tp_dict[x], types))
    
    plot_connect(fn_out, pos_nodes_crys, tp_labels, nodes, adj)

def plot_car(nodes, adj, df_all, fn_out, crys2car):
   
    pos_nodes_car = []
    types = []
    for node in nodes:
        ind_node = node
        pos_nodes_car.append(np.dot(crys2car, np.array(df_all[df_all["ind_unique"]==ind_node]["position_crys"].values[0])))
        types.append(df_all[df_all["ind_unique"]==ind_node]["type"].values[0])
    pos_nodes_car = np.array(pos_nodes_car)
    tp_dict = {"nuc" : 0, "nna" : 1, "b" : 2}
    tp_labels=list(map(lambda x: tp_dict[x], types))

    plot_connect(fn_out, pos_nodes_car, tp_labels, nodes, adj)
