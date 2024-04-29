#! /usr/bin/env python3

import os
import sys
from numpy import absolute


def get_hdos(dir_pdos, e_fermi, verbose=False):
    e_fermi = round(e_fermi,3)
    print("Fermi energy : {:.3f}".format(e_fermi))
    if os.path.exists(dir_pdos): 
        if not any([(".pdos_" in file) for file in os.listdir(dir_pdos)]):
            raise ValueError("Files containing projected DOS do not exist in {}".format(dir_pdos))
    else:
        raise ValueError("{}: directory does not exist.".format(dir_pdos))

    os.system("grep {:.3f} {}/*.pdos_* > pdos_fermi.out".format(e_fermi, dir_pdos))
    hdos = 0
    nh = 0
    atmdos = 0
    with open("pdos_fermi.out", "r") as f:
        for i, line in enumerate(f):
            if i==0:
                e_fermi_1 = float(line.split()[1])
                assert absolute(e_fermi-e_fermi_1)<1e-3
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
    
    return hdos/totpdos


