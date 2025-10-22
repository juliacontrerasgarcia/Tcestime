#!/bin/bash
#SBATCH --job-name=TcESTIME
#SBATCH --partition=thin
#SBATCH --ntasks=64
#SBATCH --nodes=1
#SBATCH --cpus-per-task=1
#SBATCH --time=00-07:00:00

$SCRATCH

export OMP_NUM_THREADS=${SLURM_CPUS_PER_TASK}
export MKL_NUM_THREADS=1=${SLURM_CPUS_PER_TASK}
export MKL_DYNAMIC=FALSE


ml vasp/6.4.3/gcc-openmpi

#ml vasp/6.4.3/gcc-openmpi418

srun vasp_std

efermi=$(grep "E-fermi" OUTCAR | awk '{print $3}')
emax=$( echo $efermi + 0.5 | bc)
emin=$( echo $efermi - 0.5 | bc)

#-------- dos ---------
mkdir dos
#cp ../INCAR-dos ../dos/INCAR
cd dos/
cp ../INCAR .
cp ../CHGCAR .
cp ../POSCAR .
cp ../POTCAR .
cp ../KPOINTS .

touch INCAR
echo "SYSTEM = sys" > INCAR
echo "LWAVE = .FALSE." > INCAR
echo "PREC = Accurate" >> INCAR
echo "ICHARG=11" >> INCAR
echo "ENCUT = 700" >> INCAR
echo "ISMEAR = 1;  SIGMA = 0.1" >> INCAR
echo "SYMPREC=1e-4" >> INCAR
echo "LORBIT=10" >> INCAR
echo "NPAR = 4" >> INCAR
echo "EMIN=${emin}" >> INCAR
echo "EMAX=${emax}" >> INCAR
echo "NEDOS=1000" >> INCAR

srun vasp_std

cd ../

#------ Tc ---------
ml intel-compilers/2023.2.1
conda init
source /softs/tools/conda/2024.10/etc/profile.d/conda.sh
conda activate /home/barreran/store/Python

/home/barreran/store/Codes/Critic2/src/critic2 critic.in > critic.out
#python3.12 /home/barreran/store/Codes/TcEstime_sm_v2_2/TcESTIME.py critic.out --fit NN --code VASP
#mv tc.dat tc_NN.dat
