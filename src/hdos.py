#! /usr/bin/env python3

import os
import sys
import numpy as np


def get_hdos(dir_pdos, e_fermi, verbose=False):
    e_fermi = round(e_fermi,3)
    print("Fermi energy : {:.3f}".format(e_fermi))
    if os.path.exists(dir_pdos): 
        if not any([(".pdos_" in file) for file in os.listdir(dir_pdos)]):
            raise ValueError("Files containing projected DOS do not exist in {}".format(dir_pdos))
    else:
        raise ValueError("{}: directory does not exist.".format(dir_pdos))

    interpolate = False # flag is True if exact efermi is not on file (next line returns empty file)
    os.system("grep ' {:.3f}' {}/*.pdos_* > pdos_fermi.out".format(e_fermi, dir_pdos))
    hdos = 0
    nh = 0
    atmdos = 0
    with open("pdos_fermi.out", "r") as f:

        lines = f.readlines()
        if len(lines) == 0:
            # In case the exact efermi is not in the file, we will interpolate 
            print("[ERROR] No PDOS entries found exactly at the Fermi energy.")
            print("Your PDOS energy step might be too coarse or EFermi lies between grid points.")
            print("We provide an interpolated approximate value, but you can choose to recompute PDOS with a finer energy grid.")
            interpolate = True
    

    if interpolate:
        ldir = os.listdir(dir_pdos)
        for d in ldir:
            d = os.path.join(dir_pdos, d)
            if "pdos_tot" in d:
                data = np.loadtxt(d, skiprows=1)
                energies = data[:,0]
                pdos = data[:,2]
                totpdos = np.interp(e_fermi, energies, pdos) # this is where we interpolate  
            elif "pdos_atm#" in d:
                at_type = d.split("(")[1].split(")_wfc")[0] # get atomic type
                if at_type == "H":
                    nh += 1
                    data = np.loadtxt(d, skiprows=1)
                    hdos += np.interp(e_fermi, data[:,0], data[:,2])
                else: 
                    data = np.loadtxt(d, skiprows=1)
                    atmdos += np.interp(e_fermi, data[:,0], data[:,2])
        

    else:
        with open("pdos_fermi.out", "r") as f:
            for i, line in enumerate(f):
                if i==0:
                    e_fermi_1 = float(line.split()[1])
                    assert np.absolute(e_fermi-e_fermi_1)<1e-3
                if "wfc" in line: #filter line with tot dos
                    at_type = line.split("(")[1].split(")_wfc")[0] # get atomic type
                    if at_type=="H":
                        hdos += float(line.split()[2])
                        nh += 1
                    else:
                        atmdos += float(line.split()[2])
                else:
                    totpdos = float(line.split()[3])
            n_orb = i   # number of orbitals is number of lines minus one

    if verbose:
        print("Coputing H_DOS ...")
        print(" Total number of orbitals  :  {}".format(n_orb))
        print(" Total PDOS                :  {:.5f}".format(totpdos))
        print(" Summed PDOS               :  {:.5f}".format(hdos+atmdos))
        print(" ")
        print(" Total number of hydrogens :  {}".format(nh))
        print(" Total contribution of H   :  {:.5f}".format(hdos))
        print(" H_DOS                     :  {:.5f}".format(hdos/(totpdos)))
        print("")
   
    # --- Prevent division by zero and give user feedback ---
    if totpdos == 0 or abs(totpdos) < 1e-10:
        print("Total DOS at the Fermi energy is zero. No H_DOS value will be provided.")
        return None


    return hdos/totpdos

