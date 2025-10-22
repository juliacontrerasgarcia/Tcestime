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
        with open("pdos_fermi.out", "r") as f:
            for i, line in enumerate(f):
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
        return hdos / totpdos

    elif code == 'VASP':
        thr = 1e-4
        at_DOS_F = []

        with open(os.path.join(dir_pdos, "dos/DOSCAR"), "r") as f:
            for i, line in enumerate(f):
                if i == 5:
                    nedos = int(line.split()[2])
                    e_fermi = round(float(line.split()[3]), 3)
                    print("Fermi energy: ", e_fermi)
                elif i > 5:
                    if i < nedos + 6 and abs(float(line.split()[0]) - e_fermi) <= thr:
                        total_DOS_F = float(line.split()[1])
                    if i > nedos + 6 and abs(float(line.split()[0]) - e_fermi) <= thr:
                        at_DOS_F.append([float(el) for el in line.split()[1:]])

        at_DOS_F = np.array(at_DOS_F)

        atoms = []
        with open(os.path.join(dir_pdos, "POSCAR"), "r") as f:
            for i, line in enumerate(f):
                if i == 5:
                    at_type = line.split()
                elif i == 6:
                    for j, n in enumerate(line.split()):
                        atoms += int(n) * [at_type[j]]

        DOS_H_F = 0
        for j, at in enumerate(atoms):
            if at == "H":
                DOS_H_F += np.sum(at_DOS_F[j])

        H_DOS = DOS_H_F / np.sum(at_DOS_F)

        print("Total DOS at Fermi:", total_DOS_F)
        print("Summed PDOS at Fermi:", np.sum(at_DOS_F))
        print("Hydrogen DOS at Fermi:", DOS_H_F)
        print("H_DOS:", H_DOS)

        return H_DOS

    else:
        raise ValueError("Unknown code. Use 'QE' or 'VASP'.")
