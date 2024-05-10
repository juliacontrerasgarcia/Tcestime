#! /usr/bin/env python

import numpy as np


def get_tc(net_val, h_frac, h_dos, molec=None, fit='meansq'):
    phi_dos = net_val * h_frac * (h_dos**(1/3))
    #t_c = 750.0 * phi_dos - 85
    if fit == 'meansq':
    	t_c = 429.3 * phi_dos - 10.4
    elif fit == 'SR2':
	t_c = 442.3 * (1- (molec-net_val)) * (h_frac**3) * (h_dos**(1./2))
    elif fit == 'SR4':
	t_c = 574.7 * net_val * (h_dos * h_frac**3 )**(1./2)

    return t_c


def write_tc(file_tc, net_val, h_frac, h_dos, molec=None, fit='meansq'):
    tc = get_tc(net_val, h_frac, h_dos, molec, fit)
    with open(file_tc, "w") as f:
        f.write("{:.2f} \n".format(tc))
