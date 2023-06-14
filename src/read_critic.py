#! /usr/bin/env python3

import numpy as np

def read_critic_out(fname):
    version=None
    with open(fname, "r") as f:
        for i, line in enumerate(f):
            if "(stable)," in line:
                version="stable"
            elif "(development)," in line:
                version="development"
            
            #if version=="stable":
            if "+ List of atomic charges and atomic numbers" in line:
                line_atomic = i
            if "+ Number of electrons" in line:
                line_elect = i
            if "* Critical point list, final report" in line:
                line_neq_cps = i
            elif "* Analysis of system bonds" in line:
                line_analy = i
            elif "B = crys to car" in line:
                line_crys2car = i
            elif "G = metric tensor" in line:
                line_metric = i
            elif "Complete CP list, bcp and rcp connectivity table" in line:
                line_all_cps = i
            elif "* Attractor connectivity matrix" in line:
                line_attr_conn = i 
            

    neq_nuc = []
    neq_nna = []
    atom_dict = {}
    elf_val_dict = {}
    n_Hs = 0
    crys2car = np.zeros((3,3))
    at_nums = []
    ind_unique = []
    translation = []
    elf_val = []
    positions_crys = []
    positions_car = []
    typ = []
    conn_bcp = []
    conn_bcp_trans = []
    conn_rcp = []
    conn_rcp_trans = []
    
    with open(fname, "r") as f:
        for i, line in enumerate(f):
            if i < line_elect-1 and i > line_atomic + 1:
                atom_dict[int(line.split()[0])] =  int(line.split()[2])
            if i < line_analy - 1 and i > line_neq_cps + 3 : 
                if line.split()[3]=="nucleus":
                    neq_nuc.append(int(line.split()[0]))
                    elf_val_dict[line.split()[0]] = float(line.split()[9])
                    if line.split()[8]=="H" or line.split()[8]=="H_":
                        n_Hs += int(line.split()[7])#1
                elif line.split()[3]=="nnattr":
                    elf_val_dict[line.split()[0]] = float(line.split()[9])
                    neq_nna.append(int(line.split()[0]))
                elif line.split()[3]=="bond":
                    elf_val_dict[line.split()[0]] = float(line.split()[9])                
                elif line.split()[4]=="ring":
                    elf_val_dict[line.split()[0]] = float(line.split()[10])                
                elif line.split()[4]=="cage":
                    elf_val_dict[line.split()[0]] = float(line.split()[10])                
            if i < line_metric and i > line_crys2car:
                crys2car[i-line_crys2car-1,:] = np.array([float(el) for el in line.split()])
            if i < line_attr_conn - 1  and i > line_all_cps + 2:
                ind_unique.append(int(line.split()[0]))
                translation.append([0, 0, 0])
                elf_val.append(elf_val_dict[line.split()[1]])
                positions_crys.append([float(el) for el in line.split()[3:6]])
                positions_car.append( list( np.dot( crys2car, np.array(positions_crys[-1]) ) ) )
                if line.split()[2]!="n":
                    typ.append(line.split()[2])
                else:
                    if int(line.split()[1]) in neq_nuc:
                        typ.append("nuc")
                        at_nums.append(atom_dict[int(line.split()[1])])
                    elif int(line.split()[1]) in neq_nna:
                        typ.append("nna")
                   
                if line.split()[2] == "b":
                    conn_bcp.append([int(line.split("(")[0].split()[-1]), int(line.split("(")[1].split()[-1])])
                    t1 = line[line.find("(")+1:line.find(")")]
                    t2 = line[line.rfind("(")+1:line.rfind(")")]
                    conn_bcp_trans.append([[int(el) for el in t1.split()], [int(el) for el in t2.split()]])
                if line.split()[2] == "r":
                    conn_rcp.append([int(line.split("(")[0].split()[-1]), int(line.split("(")[1].split()[-1])])
                    t1 = line[line.find("(")+1:line.find(")")]
                    t2 = line[line.rfind("(")+1:line.rfind(")")]
                    conn_rcp_trans.append([[int(el) for el in t1.split()], [int(el) for el in t2.split()]])

    return n_Hs, at_nums, ind_unique, translation, typ, positions_crys, positions_car, elf_val, conn_bcp, conn_bcp_trans, conn_rcp, conn_rcp_trans, crys2car
