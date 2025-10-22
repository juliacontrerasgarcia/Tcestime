#! /usr/bin/env python

import sys
import os
import subprocess as sp


def write_input(fname_cube, outdir=None, cpeps=None, nuceps=None, nucepsh=None):
    if outdir is None:
        common=os.path.splitext(fname_cube)[0]
    else:
        common=os.path.join(outdir, os.path.splitext(fname_cube)[0].split("/")[-1])
        
    # if cpeps is not None:
    #     common += "-cpeps"+str(cpeps)
    # if nuceps is not None:
    #     common += "-nuceps"+str(nuceps)
    # if nucepsh is not None:
    #     common += "-nucepsh"+str(nucepsh)

    fname_in=common+".critic.in"
    fname_out=common+".critic.out"
    with open(fname_in, "w") as f_in:
        f_in.write("crystal "+fname_cube+"\n")
        f_in.write("load "+fname_cube+"\n")
        line_auto = "AUTO "

    if cpeps is not None:
        line_auto += "CPEPS "+str(cpeps)+" "
    if nuceps is not None:
        line_auto += "NUCEPS "+str(nuceps)+" "
    if nucepsh is not None:
        line_auto += "NUCEPSH "+str(nucepsh)+" "
    
    line_auto += " \n"
    with open(fname_in, "a") as f_in:
        f_in.write(line_auto)

    return fname_in, fname_out
        
def run_critic(fname_in, fname_out, critic2=None):
    if critic2 == None:
        critic2 = sp.getoutput("which critic2")
    os.system(critic2 + " " + fname_in + " | tee " + fname_out + " >/dev/null ")
