#! /usr/bin/env python

import numpy as np
import pickle
import os

def get_tc(net_val, h_frac, h_dos, molec=None, fit='leastsq'):
    phi_dos = net_val * h_frac * (h_dos**(1/3))
    if fit == 'leastsq':
        t_c = 456.34 * phi_dos - 9.46
        eq_tc = "Tc^{leastsq} = 456.34 * phi * h_f * (h_dos)^(1/3) - 9.46"
    elif fit == 'SR2':
        t_c = 442.3 * (1- (molec-net_val)) * (h_frac**3) * (h_dos**(1./2))
        eq_tc = "Tc^{SR2} = 442.3 * (1 - (phis - phi)) * h_f^3 * (h_dos)^(1/2)"
    elif fit == 'SR4':
        t_c = 574.7 * net_val * (h_dos * h_frac**3 )**(1./2)
        eq_tc = "Tc^{SR4} = 574.7 * phi * ( h_dos * h_f^3 )^(1/2)"

    elif fit == 'GBR':
        this_dir = os.path.dirname(os.path.abspath(__file__))
        with open(this_dir+"/gradient_boosting_model.pkl", 'rb') as file:
            model = pickle.load(file)
        
        input_data=[[net_val, h_frac, h_dos, molec]]
        t_c=model.predict(input_data)[0]
        eq_tc = "Tc^{GBR} is computed using a Gradient Boosting Regression model"

    return t_c, eq_tc


def write_tc(file_tc, net_val, h_frac, h_dos, molec=None, fit='leastsq'):
    tc, eq_tc = get_tc(net_val, h_frac, h_dos, molec, fit)
    with open(file_tc, "w") as f:
        f.write("{:.2f} \n".format(tc))
