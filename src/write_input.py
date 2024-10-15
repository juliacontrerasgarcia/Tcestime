#! /usr/bin/env python

import sys
import os
import subprocess as sp


def write_input(fname_in, outdir=None, cpeps=None, nuceps=None, nucepsh=None):
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

        
def run_critic(fname_in, fname_out, critic2=None):
    if critic2 == None:
        critic2 = sp.getoutput("which critic2")
    os.system(critic2 + " " + fname_in + " | tee " + fname_out + " >/dev/null ")
