#!/usr/bin/env python3
import os
import sys
import numpy as np

def get_hdos(dir_pdos, e_fermi, verbose=False):
    """
    Calculate the hydrogen contribution to the density of states (HDOS) at the Fermi energy.
    If the exact Fermi energy is not found in the files, interpolate the DOS values.

    Args:
        dir_pdos (str): Directory containing projected DOS files.
        e_fermi (float): Fermi energy level.
        verbose (bool): If True, print additional debug information.

    Returns:
        float: Ratio of hydrogen DOS to total DOS at the Fermi energy, or None if total DOS is zero.
    """
    e_fermi = float(e_fermi)
    print("Fermi energy : {:.3f}".format(e_fermi))

    # --- Check if directory exists ---
    if not os.path.exists(dir_pdos):
        raise ValueError("{}: directory does not exist.".format(dir_pdos))

    # --- List all files in the directory and filter for PDOS files ---
    try:
        files = [f for f in os.listdir(dir_pdos) if ".pdos_" in f]
    except OSError as e:
        raise ValueError("Could not list files in {}: {}".format(dir_pdos, e))
    if not files:
        raise ValueError("Files containing projected DOS do not exist in {}".format(dir_pdos))

    # --- Initialize variables ---
    hdos = 0.0    # Hydrogen DOS
    nh = 0        # Number of hydrogen orbitals
    atmdos = 0.0  # DOS from other atoms
    totpdos = 0.0 # Total DOS
    n_orb = 0     # Number of orbitals processed
    output_lines = []  # Store lines for debugging output
    interpolate = True  # Flag: assume interpolation is needed unless exact match is found

    # --- Step 1: Try to find exact matches for e_fermi in files ---
    for filename in files:
        filepath = os.path.join(dir_pdos, filename)
        #if filename == "pdos_fermi.out": continue  # Skip the output file
        found_val = None
        found_line = None
        try:
            with open(filepath, "r") as f:
                for line in f:
                    if line.strip().startswith("#"): continue  # Skip comment lines
                    parts = line.split()
                    if len(parts) < 2: continue  # Skip malformed lines
                    try:
                        e_curr = float(parts[0])  # Extract energy value
                        # Check if energy is close to Fermi energy (within 0.005 eV tolerance)
                        if abs(e_curr - e_fermi) < 0.001:
                            found_val = np.sum([float(el) for el in parts[2:]])  # Extract PDOS value
                            found_line = line
                            interpolate = False  # Exact match found, no need to interpolate
                            break
                    except ValueError:
                        continue  # Skip lines that can't be converted to float
        except Exception as e:
            print(f"Warning: Could not read {filename}: {e}")
            continue

        # --- If a matching energy was found, process the DOS value ---
        if found_val is not None:
            n_orb += 1
            output_lines.append(f"{filepath}:{found_line}")  # Store for debugging
            if "wfc" in filename:
                if "(H)" in filename:
                    hdos += found_val  # Add to hydrogen DOS
                    nh += 1
                else:
                    atmdos += found_val  # Add to other atoms' DOS
            elif "tot" in filename or "pdos_tot" in filename:
                totpdos = found_val  # Store total DOS

    # --- Step 2: If no exact match, interpolate DOS values ---
    if interpolate:
        print("[INFO] No PDOS entries found exactly at the Fermi energy.")
        print("Your PDOS energy step might be too coarse or EFermi lies between grid points.")
        print("We provide an interpolated approximate value, but you can choose to recompute PDOS with a finer energy grid.")
        for filename in files:
            filepath = os.path.join(dir_pdos, filename)
            try:
                data = np.loadtxt(filepath, skiprows=1)
                energies = data[:, 0]
                # Use column 2 for PDOS if there is only one orbital, otherwise sum
                pdos = data[:, 2] if data.shape[1] == 2 else np.sum(data[:, 2:], axis=1)
                if "tot" in filename or "pdos_tot" in filename:
                    totpdos = np.interp(e_fermi, energies, pdos)  # Interpolate total DOS
                elif "wfc" in filename:
                    # Extract atomic type from filename (e.g., "pdos_atm#1(H)_wfc")
                    at_type = filename.split("(")[1].split(")_wfc")[0]
                    if at_type == "H":
                        hdos += np.interp(e_fermi, energies, pdos)  # Interpolate hydrogen DOS
                        nh += 1
                    else:
                        atmdos += np.interp(e_fermi, energies, pdos)  # Interpolate other atoms' DOS
            except Exception as e:
                print(f"Warning: Could not interpolate {filename}: {e}")
                continue

    # --- Write debug output to pdos_fermi.out ---
    try:
        with open("pdos_fermi.out", "w") as f_out:
            f_out.writelines(output_lines)
    except Exception:
        pass  # Silently fail if writing is not possible

    # --- Prevent division by zero ---
    if totpdos == 0 or abs(totpdos) < 1e-10:
        print("Total DOS at the Fermi energy is zero. No H_DOS value will be provided.")
        return None

    # --- Verbose output ---
    if verbose:
        print("Computing H_DOS ...")
        print(f" Total number of orbitals  :  {n_orb}")
        print(f" Total PDOS                :  {totpdos:.5f}")
        print(f" Summed PDOS               :  {(hdos+atmdos):.5f}")
        print(f" Total number of hydrogens :  {nh}")
        print(f" Total contribution of H   :  {hdos:.5f}")
        print(f" H_DOS                     :  {(hdos/totpdos):.5f}")

    # --- Return the ratio of hydrogen DOS to total DOS ---
    return hdos/totpdos
