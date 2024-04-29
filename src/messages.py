#! /usr/bin/env python

import numpy as np
from src.get_tc import get_tc

def print_tc(net_val, h_frac, h_dos):
    t_c = get_tc(net_val, h_frac, h_dos)
    if t_c >= 0:
        #print("Hydrogen fraction: {:.3f}".format(h_frac))
        #print("Given H_DOS: {}".format(h_dos))
        print("Critical temperature: {:.2f}K +/- 65K".format(t_c))
        print("")
    else:
        raise ValueError("Found temperature is negative, please check the H_DOS value given.")

def print_no_netval():
    print("")
    print("We are not able to provide a networking value for this system. We are currently working on improving TcESTIME and broaden its applicability to these types of systems.")
    #print("If you have further questions about this issue, please contact trinidad.novoa_aguirre@upmc.fr.")

def print_netval(net_val):
    #print("")
    print("Networking value: {}".format(net_val))
    #print("** Be careful, if there is molecular Hydrogen in your system, this value might be underestimated.")
     
def print_hdos(h_dos):
    print("H_DOS: {:.3f}".format(h_dos))

def print_hf(h_frac):
    print("H_f: {:.3f}".format(h_frac))
