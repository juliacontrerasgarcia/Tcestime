#! /usr/bin/env python3

#Tcestime provides a critical temperature estimation for hydrogen based superconductors.
#Copyright (C) 2023, TRINIDAD NOVOA*, Yvon Maday and Julia Contreras-Garcia.
#Please cite xxxx

    #This program is free software: you can redistribute it and/or modify
    #it under the terms of the GNU General Public License as published by
    #the Free Software Foundation, either version 3 of the License, or
    #(at your option) any later version.

    #This program is distributed in the hope that it will be useful,
    #but WITHOUT ANY WARRANTY; without even the implied warranty of
    #MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    #GNU General Public License for more details.

    #You should have received a copy of the GNU General Public License
    #along with this program.  If not, see <https://www.gnu.org/licenses/>.

import time
import os
import sys
import argparse
from src.netval import *
from src.messages import *
from src.get_dependencies import get_dependencies
from src.write_input import *
from src.get_tc import *
from src.hdos import *

time0 = time.time()

parser = argparse.ArgumentParser(description='Get the critical temperature of given system.')
data_file_parse = parser.add_argument('fname', type=str, help='File containing the data (either .cube or .out).')
h_dos_parse = parser.add_argument('--hdos', type=float, help='H_DOS value to be considered for T_c.')
pdos_dir_parse = parser.add_argument('--dpdos', type=str, help='Directory where to find pdos files to get H_DOS (*.pdos_*). Working dir is default.')
efermi_parse = parser.add_argument('--efermi', type=float, help='Fermi energy')
phi_parse = parser.add_argument('--phi', type=float, help='Fermi energy')
fit_parse = parser.add_argument('--fit', type=str, help="Fit to estimate Tc ('leastsq', 'SR2', or 'SR4'). Default is 'leastsq'.")
outdir_parse = parser.add_argument('--odir', type=str, help='Directory for output files.')
critic_parse = parser.add_argument('--critic2', type=str, help='Path to critic executable.')
plot_parse = parser.add_argument('--plot', type=bool, help='Plot network of critical points. Default is False.')
args = parser.parse_args()

data_file = args.fname
h_dos = args.hdos
pdos_dir = args.dpdos
e_fermi = args.efermi
net_val = args.phi
fit = args.fit
outdir = args.odir
critic2_path = args.critic2
plot = args.plot

work_dir = os.getcwd()

verbose = False      # True is for debugging
connect_core_nnas = True   # always keep this True




if outdir is None:
    outdir = os.path.dirname(data_file) 

if getattr(sys, 'frozen', False):
    application_path = sys._MEIPASS
else:
    application_path = os.path.dirname(os.path.abspath(__file__))

# Set default fit to least squares
if fit is None:
    fit = 'leastsq'

# Check the type of input file
if os.path.splitext(data_file)[-1]==".cube":
    # If it is a cube file we run critic2
    fn_in = os.path.splitext(os.path.basename(data_file))[0]+".critic.in"
    fn_out = os.path.splitext(os.path.basename(data_file))[0]+".critic.out"
    write_input(fn_in, data_file, cpeps=0.3, nucepsh=0.6)
    run_critic(fn_in, fn_out, critic2=critic2_path)    

else:
    # fn_out is the critic output file
    fn_out = data_file



# We begin by getting h_dos if it was not given
if h_dos is not None:
    print_hdos(h_dos)
#elif pdos_dir is not None:
elif e_fermi is not None:
    if pdos_dir is not None:
        h_dos = get_hdos(pdos_dir, e_fermi)
        print_hdos(h_dos)
    else:
        h_dos = get_hdos(work_dir, e_fermi)
        print_hdos(h_dos)
else:
    raise ValueError("Either the value of the Fermi energy or the value of H_DOS must be provided.")


# We get the networking value and print it
if net_val is not None:
    placeholder, h_frac, anti_phi = netval(fn_out, verbose=verbose, connect_core_nnas=connect_core_nnas, plot=plot)
else:
    net_val, h_frac, anti_phi =  netval(fn_out, verbose=verbose, connect_core_nnas=connect_core_nnas, plot=plot)

if net_val is not None:
    print_netval(net_val)
else:
    #print_no_netval()
    print_netval(0.0)

print_hf(h_frac)
if h_dos is not None and net_val is not None:
    print_tc(net_val, h_frac, h_dos, molec=anti_phi, fit=fit)
    write_tc(os.path.join(outdir, "tc.dat"), net_val, h_frac, h_dos, molec=anti_phi, fit=fit)


print("Time: {:.2f} s".format(time.time()-time0))

