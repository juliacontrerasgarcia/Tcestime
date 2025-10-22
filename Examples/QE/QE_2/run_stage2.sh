#!/bin/bash
#MSUB -r CaYH20
#MSUB -n 2
#MSUB -T 1800
#MSUB -A gen15069
#MSUB -q rome
#MSUB -m scratch
#MSUB -Q test

ml purge
ml intel/20.0.0
source /ccc/cont003/home/unisorbo/barreran/work/Anaconda3/bin/activate
conda activate myenv
python3.12 /ccc/cont003/dsku/blanchet/home/user/unisorbo/barreran/scratch/Systems_TcEstime/PW91/cube_tool.py elf-rescale CaYH20.ELF.cube CaYH20_ok.ELF.cube
/ccc/cont003/home/unisorbo/barreran/work/Codes/Critic2/src/critic2 critic.in > critic.out
