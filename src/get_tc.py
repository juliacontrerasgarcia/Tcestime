#! /usr/bin/env python

import numpy as np


def get_tc(net_val, h_frac, h_dos):
    phi_dos = net_val * h_frac * (h_dos**(1/3))
    #t_c = 750.0 * phi_dos - 85
    t_c = 429.3 * phi_dos - 10.4
    return t_c


def write_tc(file_tc, net_val, h_frac, h_dos):
    tc = get_tc(net_val, h_frac, h_dos)
    with open(file_tc, "w") as f:
        f.write("{:.2f} \n".format(tc))
