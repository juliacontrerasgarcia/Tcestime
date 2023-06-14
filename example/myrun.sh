#!/bin/bash
#MSUB -r tc_H3S
#MSUB -n 32
#MSUB -T 3600
#MSUB -A gen7539
#MSUB -q rome
set -x

module load python3
export PYTHONPATH=/ccc/cont003/home/unipoiti/frapperg/scratch/tnovoa/TcESTIME
export CRITIC_HOME=/ccc/cont003/home/unipoiti/frapperg/scratch/tnovoa/critic2
name="H3S.ELF"
hdos=0.48732
this_dir="/ccc/cont003/home/unipoiti/frapperg/scratch/tnovoa/TcESTIME/example"


#------ Tc ---------
touch ${name}.critic.in
echo "crystal ${this_dir}/${name}.cube" > ${name}.critic.in
echo "load ${this_dir}/${name}.cube" >> ${name}.critic.in
echo "AUTO CPEPS 0.3 NUCEPSH 0.5" >> ${name}.critic.in

/ccc/cont003/home/unipoiti/frapperg/scratch/tnovoa/critic2/bin/critic2 < ${name}.critic.in > ${name}.critic.out
python3 /ccc/cont003/home/unipoiti/frapperg/scratch/tnovoa/TcESTIME/TcESTIME.py --hdos $hdos ${name}.critic.out > netval.out

