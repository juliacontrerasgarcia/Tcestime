def get_hdos(dir_pdos, e_fermi, code='QE', verbose=False):
    import numpy as np
    from numpy import absolute
    import os

    if code == 'QE':
        e_fermi = round(e_fermi,3)
        print("Fermi energy : {:.3f}".format(e_fermi))
        if os.path.exists(dir_pdos): 
            if not any([(".pdos_" in file) for file in os.listdir(dir_pdos)]):
                raise ValueError("Files containing projected DOS do not exist in {}".format(dir_pdos))
        else:
            raise ValueError("{}: directory does not exist.".format(dir_pdos))

        os.system(f"grep ' {e_fermi:.3f}' {dir_pdos}/*.pdos_* > pdos_fermi.out")

        hdos = 0
        nh = 0
        atmdos = 0
        totpdos = None

        with open("pdos_fermi.out", "r") as f:
            lines = f.readlines()
        
        if len(lines) == 0:
            print("[ERROR] No PDOS entries found exactly at the Fermi energy.")
            print("Your PDOS energy step might be too coarse or EFermi lies between grid points.")
            print("Please recompute PDOS with a finer energy grid or check EF.")
            return None

        #for i, line in enumerate(f):
        for i, line in enumerate(lines):
            if i == 0:
                e_fermi_1 = float(line.split()[1])
                assert absolute(e_fermi - e_fermi_1) < 1e-3
            if "wfc" in line:
                at_type = line.split("(")[1].split(")_wfc")[0]
                if at_type == "H":
                    hdos += float(line.split()[2])
                    nh += 1
                else:
                    atmdos += float(line.split()[2])
            else:
                totpdos = float(line.split()[3])
        if verbose:
            print("Computing H_DOS ...")
            print("Total H contribution: {:.5f}".format(hdos))
            print("Total PDOS: {:.5f}".format(totpdos))
 
        # --- Prevent division by zero and give user feedback ---
        if totpdos == 0 or abs(totpdos) < 1e-10:
            return None        

        return hdos / totpdos

    elif code == 'VASP':
        thr = 1e-4
        at_DOS_F = []
        total_DOS_F = None  # ← para detectar si nunca se encontró EF

        doscar = os.path.join(dir_pdos, "dos", "DOSCAR")
        poscar = os.path.join(dir_pdos, "POSCAR")

        if not os.path.isfile(doscar):
            print(f"[ERROR] DOSCAR not found at: {doscar}")
            return None
        if not os.path.isfile(poscar):
            print(f"[ERROR] POSCAR not found at: {poscar}")
            return None

        # Leer DOSCAR y capturar DOS total y por-átomo en EF (con tolerancia thr)
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

        # Si no hubo ninguna fila a EF dentro del umbral
        if total_DOS_F is None or len(at_DOS_F) == 0:
            print("[ERROR] No DOS entries found at the Fermi energy within the threshold.")
            print("Your DOS energy step might be too coarse or EF lies between grid points.")
            print("Please recompute DOS/PDOS with a finer energy grid or use a nearest-energy approach.")
            return None

        at_DOS_F = np.array(at_DOS_F)

        # Leer especies y multiplicidades desde POSCAR
        atoms = []
        with open(poscar, "r") as f:
            for i, line in enumerate(f):
                if i == 5:
                    at_type = line.split()
                elif i == 6:
                    for j, n in enumerate(line.split()):
                        atoms += int(n) * [at_type[j]]

        # Sumar contribución de H en EF
        DOS_H_F = 0.0
        for j, at in enumerate(atoms):
            if at == "H":
                DOS_H_F += np.sum(at_DOS_F[j])

        denom = np.sum(at_DOS_F)
        if denom == 0 or abs(denom) < 1e-12:
            print("[ERROR] Summed PDOS at the Fermi energy is zero.")
            print("Your system might be non-metallic or EF lies in a gap. Please check DOS/PDOS.")
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
