#!/bin/bash
#SBATCH -J ejemplo
#SBATCH -p general
#SBATCH -n 10
#SBATCH --ntasks-per-node=10
#SBATCH --mem-per-cpu=2000
#SBATCH -t 0-05:00:00 

module purge
module purge
module load intel/2018.04 QuantumESPRESSO/6.3

#srun pw.x < scf.in > scf.out
#srun pw.x < nscf.in > nscf.out
srun pp.x < pp.in > pp.out
srun projwfc.x < pdos.in > pdos.out

