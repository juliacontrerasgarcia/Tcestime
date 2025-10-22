#! /usr/bin/env python

import numpy as np
import pickle
import os
from .NN_av import predict as nn_predict

def get_tc(net_val, h_frac, h_dos, molec=None, fit='leastsq', code='QE'):
    """
    Compute critical temperature Tc using various models.
    
    Parameters:
        net_val (float): networking value (phi)
        h_frac (float): hydrogen fraction (Hf)
        h_dos (float): hydrogen projected DOS at EF (HDOS)
        molec (float or None): molecularity index (required for some models)
        fit (str): model type ('leastsq', 'SR2', 'SR4', 'GBR', 'NN')
        
    Returns:
        t_c (float): predicted critical temperature in K
        eq_tc (str): string representing the formula or model used
    """
    phi_dos = net_val * h_frac * (h_dos**(1/3))

    if fit == 'leastsq':
        t_c = 456.34 * phi_dos - 9.46
        eq_tc = "Tc^{leastsq} = 456.34 * phi * Hf * (HDOS)^{1/3}"

    elif fit == 'SR2':
        t_c = 442.3 * (1 - (molec - net_val)) * (h_frac**3) * (h_dos**0.5)
        eq_tc = "Tc^{SR2} = 442.3 * (1 - (phis - phi)) * Hf^3 * (HDOS)^{1/2}"

    elif fit == 'SR4':
        t_c = 574.7 * net_val * (h_dos * h_frac**3)**0.5
        eq_tc = "Tc^{SR4} = 574.7 * phi * (HDOS * Hf^3)^{1/2}"

    elif fit == 'SR5':
        t_c = 422.2 * (27/4) * (molec**2 - molec**3)  * (h_frac**3) * (net_val * h_dos)**(1/3) + 5.5
        eq_tc = "Tc^{SR5} = 422.2 * (27/4) * (phis^2 - phis^3)  * (Hf^3) * (phi * HDOS )^{1/3} + 5.5"

    elif fit == 'GBR':
        this_dir = os.path.dirname(os.path.abspath(__file__))
        with open(os.path.join(this_dir, "gradient_boosting_model.pkl"), 'rb') as file:
            model = pickle.load(file)
        input_data = [[net_val, h_frac, h_dos, molec]]
        t_c = model.predict(input_data)[0]
        eq_tc = "Tc^{GBR} is computed using a Gradient Boosting Regression model"

    elif fit == 'NN':
        # Neural network expects input: [NET, MolecularityIndex, Hf, HDOS]
        #input_data = [net_val, molec, h_frac, h_dos]
        #t_c = nn_predict(input_data)
        #eq_tc = "Tc^{NN} is predicted using a neural network (ONNX model)"
        input_data = [net_val, molec, h_frac, h_dos]
        t_c = nn_predict(input_data, code=code)
        eq_tc = f"Tc^{{NN}}_{{{code}}} predicted with neural network ensemble trained on {code} data"

    else:
        raise ValueError(f"Unknown fit type: {fit}")

    return t_c, eq_tc


def write_tc(file_tc, net_val, h_frac, h_dos, molec=None, fit='leastsq', code='QE'):
    tc, eq_tc = get_tc(net_val, h_frac, h_dos, molec, fit, code)
    """
    Write predicted Tc to a file.
    """
    tc, eq_tc = get_tc(net_val, h_frac, h_dos, molec, fit)
    with open(file_tc, "w") as f:
        f.write("{:.2f} \n".format(tc))
