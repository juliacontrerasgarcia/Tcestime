#!/bin/bash
#MSUB -r CaYH20
#MSUB -n 64
#MSUB -T 1800
#MSUB -A gen15069
#MSUB -q hybrid
#MSUB -m scratch
#MSUB -Q test

module purge
module load gnu/11 mpi/openmpi/4 espresso/7.2.0

ccc_mprun -n 64 pw.x -npool 4 -i scf.in > scf.out
ccc_mprun -n 64 pw.x -npool 4 -i nscf.in > nscf.out
ccc_mprun -n 16 pp.x -i pp.in > pp.out
ccc_mprun -n 16 projwfc.x -i pdos.in > pdos.out
#rm -rf *.wfc* 
#rm -rf *.save 
#rm -rf *.xml
