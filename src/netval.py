#! /usr/bin/env python3

import time
import os
import sys
import pandas as pd
import numpy as np
from src.tree import *
from src.read_critic import read_critic_out
from src.plot import *
from src.core_r_dat import *


def netval(fname, verbose=False, connect_core_nnas=True, plot=False):

    fn_dir = os.path.dirname(os.path.abspath(fname))
    fn_common = os.path.splitext(os.path.basename(fname))[0]
    
    # This function gets all info from critic2 output file
    n_Hs, at_nums, ind_unique, translation, cp_type, position_crys, position_car, elf_val, conn_bcp, conn_bcp_trans, conn_rcp, conn_rcp_trans, crys2car = read_critic_out(fname)
    N = len(ind_unique)

    N_nuc = cp_type.count("nuc")
    N_nna = cp_type.count("nna")
    N_bcp = cp_type.count("b")

    h_frac = n_Hs / N_nuc
    
    # Some quick checks
    if len(at_nums) != N_nuc:
        raise ValueError("The atomic number list is inconsistent with the number of nuclei.")
    if len(conn_bcp) != N_bcp:
        raise ValueError("The bcp connections list is inconsistent with the number of bond critical points.")

    at_nums_all = [None] * N
    conn_all = [None] * N
    conn_all_trans = [None] * N
    j_at=0
    j_conn1=0
    j_conn2=0
    for i, tp in enumerate(cp_type):
        if tp=="nuc":
            at_nums_all[i] = at_nums[j_at]
            j_at+=1
        if tp=="b":
            conn_all[i] = conn_bcp[j_conn1]
            conn_all_trans[i] = conn_bcp_trans[j_conn1]
            j_conn1+=1

    # Dataframe with all the info in the unit cell
    df_000 = pd.DataFrame(
        {
            "ind_unique": ind_unique,
            "type" : cp_type,
            "translation" : translation,
            "position_crys" : position_crys,
            "position_car" : position_car,
            "elf_val" : np.round(elf_val, 2),
            "at_nums" : at_nums_all,
            "connections" : conn_all,
            "connections trans" : conn_all_trans,
        },
        #index=ind_unique
    )
    
    df_all = df_000

    # separate DFs according to type
    nuc_df = df_all[df_all["type"]=="nuc"]
    nna_df = df_all[df_all["type"]=="nna"]


    if connect_core_nnas:
        core_rad = core_radii()
        nna_core_dict = {}
        for i_nuc, pos_nuc in nuc_df["position_car"].iteritems():
            nuc = nuc_df.loc[i_nuc]["ind_unique"]
            if int(nuc_df.loc[i_nuc]["at_nums"]) in core_rad.keys():
                for i_nna, pos_nna in nna_df["position_car"].iteritems():
                    nna = nna_df.loc[i_nna]["ind_unique"]
                    if np.linalg.norm(np.array(pos_nuc)-np.array(pos_nna)) < core_rad[int(nuc_df.loc[i_nuc]["at_nums"])]:
                        nna_core_dict[nna] = nuc


    # These are different because we will only take some pts
    bcp_df1 = df_all[df_all["type"]=="b"]

    # Values through which we loop
    elf_set = np.flip(np.sort(np.unique(bcp_df1["elf_val"].values)))
    translations = []
    netval=0
    dim1 = False
    dim2 = False
    dim3 = False
    anti_phi = 0.0
    for isoval in elf_set:
        if verbose:
            print("")
            print("ELF isoval: ", isoval)
        bcp_df = bcp_df1[bcp_df1["elf_val"]>=isoval]
        edge_dict = {}

        nodes = set()
        for ind_bcp, conn in bcp_df["connections"].iteritems():
            if len(conn) > 0:
                edge = (bcp_df.loc[ind_bcp]["connections"][0], bcp_df.loc[ind_bcp]["connections"][1])
                if connect_core_nnas:
                    if edge[0] in nna_core_dict.keys():
                        edge = (nna_core_dict[edge[0]], edge[1])
                    if edge[1] in nna_core_dict.keys():
                        edge = (edge[0], nna_core_dict[edge[1]])
                if edge in edge_dict.keys():
                    edge_dict[edge] += [[bcp_df.loc[ind_bcp]["connections trans"][1][i] - bcp_df.loc[ind_bcp]["connections trans"][0][i] for i in range(3)]]
                elif tuple(reversed(edge)) in edge_dict.keys():
                    edge_dict[tuple(reversed(edge))] += [[bcp_df.loc[ind_bcp]["connections trans"][0][i] - bcp_df.loc[ind_bcp]["connections trans"][1][i] for i in range(3)]]
                else:
                    edge_dict[edge] = [[bcp_df.loc[ind_bcp]["connections trans"][1][i] - bcp_df.loc[ind_bcp]["connections trans"][0][i] for i in range(3)]]
                for node in edge:
                    nodes.add(node)

        nodes = list(nodes)
        if verbose:
            print("Nodes: ", nodes)
        adj = adjacency(nodes, edge_dict, verbose=verbose)
        at_nums = []
        for n in nodes:
            for i_node, node in df_all["ind_unique"].iteritems():
                if node==n:
                    at_nums.append(df_all.loc[i_node]["at_nums"])
                if len(at_nums)==len(nodes):
                    break
        translations, rank, dim1, dim2, dim3, anti_phi = tree(nodes, edge_dict, translations, at_nums, isoval, dim1, dim2, dim3, anti_phi, verbose=verbose)
        #plot_uc(nodes, adj, df_all, fn_dir+"/Figures/"+fn_common+"-"+str(isoval)+".png")
        if rank >=3:
            netval=isoval
            if plot:
                os.system("mkdir "+fn_dir+"/Figures")
                plot_uc(nodes, adj, df_all, fn_dir+"/Figures/"+fn_common+"-"+str(isoval)+".png")
            return netval, h_frac

    
    #print("Networking value: {}, Time: {}".format(netval, time.time()-time0))
    return None, h_frac
