#! /usr/bin/env python3

# TcESTIME provides a critical temperature estimation for hydrogen-based superconductors.
# Copyright (C) 2023, TRINIDAD NOVOA*, Yvon Maday and Julia Contreras-Garcia.
# Please cite:

# 1. TcESTIME: predicting high-temperature hydrogen-based superconductors. Chemical Science, 2025, 16, 57-68.
# 2. Strong correlation between electronic bonding network and critical temperature in hydrogen-based superconductors. Nature communications, 2021, 12, 5381.

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import time
import os
import sys
import argparse

# Add the src folder to PYTHONPATH
sys.path.append('/ccc/cont003/home/unisorbo/barreran/work/Codes/TcESTIME_v2/src')

from src.netval import *
from src.messages import *
from src.get_dependencies import get_dependencies
from src.write_input import *
from src.get_tc import *
from src.hdos import *

time0 = time.time()

parser = argparse.ArgumentParser(description='Get the critical temperature of given system.')

parser.add_argument('fname', type=str, help='File containing the data (either .cube or .out).')
parser.add_argument('--hdos', type=float, help='H_DOS value to be considered for T_c.')
parser.add_argument('--dpdos', type=str, help='Directory where to find pdos files to get H_DOS (*.pdos_*). Working dir is default.')
parser.add_argument('--efermi', type=float, help='Fermi energy')
#parser.add_argument('--fit', type=str, help="Fit to estimate Tc ('leastsq', 'SR2', 'SR4', 'GBR', or 'NN'). Default is 'NN'.")
parser.add_argument(
    '--fit',
    type=str,
    default='NN',
    help="Fit to estimate Tc ('leastsq', 'SR2', 'SR4', 'GBR', or 'NN'). Default is 'NN'. "
         "Note: for --code VASP only 'NN' is supported."
)
parser.add_argument('--odir', type=str, help='Directory for output files.')
parser.add_argument('--critic2', type=str, help='Path to critic executable.')
parser.add_argument('--plot', type=bool, help='Plot network of critical points. Default is False.')
parser.add_argument('--code', type=str, choices=['QE', 'VASP'], default='QE', help="Code used to generate PDOS data: 'QE' (default) or 'VASP'.")
parser.add_argument('--qeout', type=str, default='nscf.out',help="QE output file to extract Fermi energy if --efermi is not provided. Default is 'nscf.out'.")

args = parser.parse_args()
code = args.code
fit = args.fit
if code.lower() == "vasp" and args.fit is not None and fit.lower() != "nn":
    from src import messages
    print(messages.error_vasp_fit(fit))
    sys.exit(1)
data_file = args.fname
h_dos = args.hdos
pdos_dir = args.dpdos
e_fermi = args.efermi
fit = args.fit
outdir = args.odir
critic2_path = args.critic2
plot = args.plot

work_dir = os.getcwd()
verbose = False
connect_core_nnas = True

fname = sys.argv[1]
if outdir is None:
    outdir = os.path.dirname(fname)

if getattr(sys, 'frozen', False):
    application_path = sys._MEIPASS
else:
    application_path = os.path.dirname(os.path.abspath(__file__))

#if fit is None:
#    fit = 'NN'

fn_out = data_file
fn_common = os.path.splitext(fn_out)[0]

# Determine H_DOS
if h_dos is not None:
    print_hdos(h_dos)
elif e_fermi is not None:
    h_dos = get_hdos(pdos_dir or work_dir, e_fermi, code=code)
    if h_dos is None:
        print("[INFO] H_DOS could not be computed.")
        print("Your system might be non-metallic or EF lies in a gap. Please check your DOS/PDOS.")
    else:
        print_hdos(h_dos)

elif code == "VASP":
    h_dos = get_hdos(pdos_dir or work_dir, None, code=code)
    if h_dos is None:
            print("[INFO] H_DOS could not be computed.")
            print("Your system might be non-metallic. Please check your DOS/PDOS.")
        else:
            print_hdos(h_dos)

elif code == "QE":
    # Extract Fermi energy from QE output file (e.g., nscf.out)
    qe_output_file = args.qeout
    try:
        with open(qe_output_file, 'r') as f:
            lines = f.readlines()
        fermi_lines = [line for line in lines if 'the Fermi energy is' in line]
        if not fermi_lines:
            raise ValueError(f"No Fermi energy found in QE output file '{qe_output_file}'.")
        e_fermi = float(fermi_lines[-1].split()[-2])  # penultimate token is the value
        print(f"Fermi energy automatically read from '{qe_output_file}': {e_fermi:.4f} eV")
        h_dos = get_hdos(pdos_dir or work_dir, e_fermi, code=code)
        if h_dos is None:
            print("[INFO] H_DOS could not be computed.")
            print("Your system might be non-metallic. Please check your DOS/PDOS.")
        else:
            print_hdos(h_dos)
    except FileNotFoundError:
        raise FileNotFoundError(f"QE output file '{qe_output_file}' not found.")

# Get network value and print
net_val, h_frac, anti_phi = netval(fn_out, verbose=verbose, connect_core_nnas=connect_core_nnas, plot=plot)
print_netval(net_val if net_val is not None else 0.0)
print_hf(h_frac)

# Verificar que todos los descriptores estén disponibles
if None in (net_val, h_frac, h_dos, anti_phi):
    print("[WARNING] One or more descriptors could not be computed (net_val, h_frac, h_dos, anti_phi). Writing 'NA' to tc.dat.")
    with open(os.path.join(outdir, "tc.dat"), "w") as f:
        f.write("NA\n")
else:
    # Todos los descriptores están presentes → calcular Tc normalmente
    print_tc(net_val, h_frac, h_dos, molec=anti_phi, fit=fit, code=code)
    write_tc(os.path.join(outdir, "tc.dat"), net_val, h_frac, h_dos, molec=anti_phi, fit=fit, code=code)

#if h_dos is not None and net_val is not None:
    #if code == "VASP":
        # Apply empirical correction to convert VASP descriptors to QE scale
    #    net_val = 0.8616 * net_val + 0.0273
    #    anti_phi = 1.0216 * anti_phi - 0.0301
    #    print(f"[VASP correction] net_val corrected = {net_val:.4f}, anti_phi corrected = {anti_phi:.4f}")

    #print_tc(net_val, h_frac, h_dos, molec=anti_phi, fit=fit)
    #write_tc(os.path.join(outdir, "tc.dat"), net_val, h_frac, h_dos, molec=anti_phi, fit=fit)

 #   print_tc(net_val, h_frac, h_dos, molec=anti_phi, fit=fit, code=code)
  #  write_tc(os.path.join(outdir, "tc.dat"), net_val, h_frac, h_dos, molec=anti_phi, fit=fit, code=code)

print("Time: {:.2f} s".format(time.time() - time0))
