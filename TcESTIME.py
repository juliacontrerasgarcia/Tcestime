#! /usr/bin/env python3

import time
import os
import sys
import argparse
from src.netval import *
from src.messages import *
from src.get_dependencies import get_dependencies
#from src.visualizer import visualizer
from src.write_input import *
from src.get_tc import *


time0 = time.time()

parser = argparse.ArgumentParser(description='Get the critical temperature of given system.')
data_file_parse = parser.add_argument('fname', type=str, help='File containing the data (either .cube or .out).')
h_dos_parse = parser.add_argument('--hdos', type=float, help='H_DOS fraction value to be considered for T_c.')
outdir_parse = parser.add_argument('--odir', type=str, help='Directory for output files.')
critic_parse = parser.add_argument('--critic2', type=str, help='Path to critic executable.')
plot_parse = parser.add_argument('--plot', type=bool, help='Plot network of critical points. Default is False.')
args = parser.parse_args()

data_file = args.fname
h_dos = args.hdos
outdir = args.odir
critic2_path = args.critic2
plot = args.plot



verbose = False #True
connect_core_nnas = True

fname = sys.argv[1]
if outdir is None:
    outdir = os.path.dirname(fname)


if getattr(sys, 'frozen', False):
    application_path = sys._MEIPASS
else:
    application_path = os.path.dirname(os.path.abspath(__file__))

    
if data_file.split(".")[-1] == "cube":
    # Check if critic2 is installed and, if not, install it
    get_dependencies()

    # Write critic2 input files and run it
    fname_cube = data_file    
    fnames_in = []
    fnames_out = []
    fname_in, fname_out = write_input(fname_cube, outdir, cpeps=0.3, nucepsh=0.5)
    fnames_in.append(fname_in)
    fnames_out.append(fname_out)

        
    for fn_in, fn_out in zip(fnames_in, fnames_out):
        print("Wrote critic2 input file : {}".format(fn_in))
        print("Running critic2...          ", end="", flush=True)
        run_critic(fn_in, fn_out, critic2=critic2_path)
        print("done")
        print("Wrote critic2 ouput file : {}".format(fn_out))
        
    #run_visualizer = True
    
elif data_file.split(".")[-1] == "out":
    fname_out = data_file

    fnames_in = []
    fnames_out = [fname_out]
    #run_visualizer = False

for fn_out in fnames_out:
    fn_common = os.path.splitext(fn_out)[0]
    
    net_val, h_frac =  netval(fn_out, verbose=verbose, connect_core_nnas=connect_core_nnas, plot=plot)
    net_vals = []
    
    if net_val is not None:
        print_netval(net_val)
        
    elif net_val is None:
        if len(fnames_in)<=1:
            print_no_netval()
        else:
            net_vals.append(net_val)

if len(fnames_in)<=1:
    if h_dos is not None and net_val is not None:
        print_tc(net_val, h_frac, h_dos)
        write_tc(os.path.join(outdir, "tc.dat"), net_val, h_frac, h_dos)
    else:
        print("")
else:
    if all([net is None for net in net_vals]):
        print_no_netval()
    else:
        net_vals = np.array(net_vals)
        net_vals = net_vals[np.where(net_vals is not None)[0]]
        min_val = min(net_vals)
        max_val = max(net_vals)
        if max_val-min_val<=0.1:
            print("")
            print("Consistent networking value (+/- 0.1)")
            print_netval(np.mean(net_vals))
            if h_dos is not None and net_val is not None:
                print_tc(net_val, h_frac, h_dos)
                write_tc(os.path.join(outdir, "tc.dat"), net_val, h_frac, h_dos)
            else:
                print("")
        else:
            print("The obtained networking values are not consistent")
            print("Obtained values: {}".format(net_vals))


run_visualizer=False
#if run_visualizer:
    # Run the visualizer
    #print("Running visulizer...          ", end="", flush=True)
    #if net_val is not None:
        #visualizer(fname_out, fname_cube, net_val)
        #os.system("python3 " + os.path.dirname(os.path.realpath(__file__)) + "/visualizer.py " + " " + fname_out + " " + fname_cube + " " + str(net_val))
    #else:
        #visualizer(fname_out, fname_cube, 0.1)
        #os.system("python3 " + os.path.dirname(os.path.realpath(__file__)) + "/visualizer.py "+  " " + fname_out + " " + fname_cube + " 0.1") 

    #print("done")


print("Time: {:.2f} s".format(time.time()-time0))
