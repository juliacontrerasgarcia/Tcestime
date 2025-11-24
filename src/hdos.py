def get_hdos(dir_pdos, e_fermi, code='QE', verbose=False):
    import numpy as np
    from numpy import absolute
    import os

    if code == 'QE':
        # Round only for printing/grep; internally keep original float EF
        e_fermi = float(e_fermi)
        e_fermi_rounded = round(e_fermi, 3)
        print("Fermi energy : {:.3f}".format(e_fermi_rounded))

        # --- Check directory existence and availability of PDOS files ---
        if os.path.exists(dir_pdos):
            if not any([(".pdos_" in file) for file in os.listdir(dir_pdos)]):
                raise ValueError(
                    "Files containing projected DOS do not exist in {}".format(dir_pdos)
                )
        else:
            raise ValueError("{}: directory does not exist.".format(dir_pdos))

        # ----------------------------------------------------------------------
        # Attempt 1: Try to find an *exact* EF match by grepping the PDOS files
        # ----------------------------------------------------------------------
        os.system(f"grep ' {e_fermi_rounded:.3f}' {dir_pdos}/*.pdos_* > pdos_fermi.out")

        hdos = 0.0      # Hydrogen DOS accumulator
        nh = 0          # Number of hydrogen orbitals encountered
        atmdos = 0.0    # Contribution from all non-H atoms
        totpdos = None  # Total DOS at EF (from pdos_tot file)

        # Read grep output
        try:
            with open("pdos_fermi.out", "r") as f:
                lines = f.readlines()
        except FileNotFoundError:
            lines = []

        # --------------------------------------------------------------
        # If exact EF matches were found → process them
        # --------------------------------------------------------------
        if len(lines) > 0:
            for i, line in enumerate(lines):
                parts = line.split()
                if len(parts) < 3:
                    continue

                if i == 0:
                    e_fermi_1 = float(parts[1])
                    assert absolute(e_fermi_rounded - e_fermi_1) < 1e-3

                # Atomic PDOS (wfc files)
                if "wfc" in line:
                    at_type = line.split("(")[1].split(")_wfc")[0]
                    if at_type == "H":
                        hdos += float(parts[2])   # LDOS of H orbital
                        nh += 1
                    else:
                        atmdos += float(parts[2])

                # Total PDOS from pdos_tot
                else:
                    # parts[3] corresponds to pdos(E) column (sum of projections)
                    if len(parts) > 3:
                        totpdos = float(parts[3])

            if verbose:
                print("Computing H_DOS (exact EF match) ...")
                print("Total H contribution: {:.5f}".format(hdos))
                print("Total PDOS: {:.5f}".format(totpdos))
                print("Number of H orbitals:", nh)

            if totpdos is None or totpdos == 0 or abs(totpdos) < 1e-10:
                print("Total DOS at the Fermi energy is zero or undefined.")
                return None

            return hdos / totpdos

        # ----------------------------------------------------------------------
        # Attempt 2: NO exact EF match found → perform linear interpolation
        # ----------------------------------------------------------------------
        print("[INFO] No PDOS entries found exactly at the Fermi energy.")
        print("[INFO] Falling back to interpolation. Consider using a finer energy grid.")

        files = [f for f in os.listdir(dir_pdos) if ".pdos_" in f]
        if not files:
            raise ValueError("Files containing projected DOS do not exist in {}".format(dir_pdos))

        hdos = 0.0
        nh = 0
        atmdos = 0.0
        totpdos = 0.0
        have_tot = False

        for fname in files:
            filepath = os.path.join(dir_pdos, fname)
            try:
                data = np.loadtxt(filepath, comments="#")
            except Exception as e:
                print(f"[WARNING] Could not read {filepath}: {e}")
                continue

            if data.ndim != 2 or data.shape[1] < 2:
                print(f"[WARNING] File {filepath} has unexpected shape={data.shape}. Skipping.")
                continue

            energies = data[:, 0]

            # ====== CASE 1: ORBITAL FILE (wfc) ======
            if "wfc" in fname:
                pdos = data[:, 1]
                if e_fermi < energies.min() or e_fermi > energies.max():
                    continue
                val = np.interp(e_fermi, energies, pdos)

                if "(" in fname and ")_wfc" in fname:
                    at_type = fname.split("(")[1].split(")_wfc")[0]
                else:
                    at_type = "X"

                if at_type == "H":
                    hdos += val
                    nh += 1
                else:
                    atmdos += val

            # ====== CASE 2: TOTAL DOS FILE (pdos_tot) ======
            elif "tot" in fname or "pdos_tot" in fname:
                # Format:  E | dos(E) | pdos(E)
                if data.shape[1] < 3:
                    print(f"[ERROR] Total DOS file {fname} does not contain 3 columns.")
                    continue

                pdos_total = data[:, 2]  # USE pdos(E) as in exact-match path

                if e_fermi < energies.min() or e_fermi > energies.max():
                    continue

                totpdos = np.interp(e_fermi, energies, pdos_total)
                have_tot = True

        if not have_tot:
            print("[ERROR] Could not determine total DOS (no pdos_tot file found).")
            return None

        if totpdos == 0 or abs(totpdos) < 1e-10:
            print("Total DOS at interpolated EF is zero.")
            return None

        if verbose:
            print("Computing H_DOS (interpolated EF) ...")
            print(f" Total number of H orbitals :  {nh}")
            print(f" Total PDOS (interpolated)  :  {totpdos:.5f}")
            print(f" H contribution (interp.)   :  {hdos:.5f}")
            print(f" H_DOS                      :  {hdos/totpdos:.5f}")

        return hdos / totpdos

    # ======================================================================
    # =========================  VASP branch  ===============================
    # ======================================================================
    elif code == 'VASP':
        thr = 1e-4
        at_DOS_F = []
        total_DOS_F = None  # Marker to detect if EF was matched

        doscar = os.path.join(dir_pdos, "dos", "DOSCAR")
        poscar = os.path.join(dir_pdos, "POSCAR")

        if not os.path.isfile(doscar):
            print(f"[ERROR] DOSCAR not found at: {doscar}")
            return None
        if not os.path.isfile(poscar):
            print(f"[ERROR] POSCAR not found at: {poscar}")
            return None

        # Read DOSCAR: capture total DOS and projected DOS at EF
        with open(doscar, "r") as f:
            for i, line in enumerate(f):
                if i == 5:
                    nedos = int(line.split()[2])
                    e_fermi = round(float(line.split()[3]), 3)
                    print("Fermi energy:", e_fermi)
                elif i > 5:
                    e_val = float(line.split()[0])
                    if i < nedos + 6 and abs(e_val - e_fermi) <= thr:
                        total_DOS_F = float(line.split()[1])
                    if i > nedos + 6 and abs(e_val - e_fermi) <= thr:
                        at_DOS_F.append([float(el) for el in line.split()[1:]])

        if total_DOS_F is None or len(at_DOS_F) == 0:
            print("[ERROR] No DOS entries found at the Fermi energy within threshold.")
            return None

        at_DOS_F = np.array(at_DOS_F)

        # Read atomic types from POSCAR
        atoms = []
        with open(poscar, "r") as f:
            for i, line in enumerate(f):
                if i == 5:
                    at_type = line.split()
                elif i == 6:
                    for j, n in enumerate(line.split()):
                        atoms += int(n) * [at_type[j]]

        # Accumulate H contribution at EF
        DOS_H_F = 0.0
        for j, at in enumerate(atoms):
            if at == "H":
                DOS_H_F += np.sum(at_DOS_F[j])

        denom = np.sum(at_DOS_F)
        if denom == 0 or abs(denom) < 1e-12:
            print("[ERROR] Summed PDOS at EF is zero (system may be insulating).")
            return None

        H_DOS = DOS_H_F / denom

        if verbose:
            print("Total DOS at Fermi:", total_DOS_F)
            print("Summed PDOS at Fermi:", denom)
            print("Hydrogen DOS at Fermi:", DOS_H_F)
            print("H_DOS:", H_DOS)

        return H_DOS

    else:
        raise ValueError("Unknown code. Use 'QE' or 'VASP'.")
