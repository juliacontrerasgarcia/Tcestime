+ SCRIPT_PID=2650185
+ /bin/bash -x /tmp/tmp.Zf4hx7YaQt
+ set +x
+ unset _mlshdbg
+ '[' 1 = 1 ']'
+ case "$-" in
+ set +x
+ unset _mlshdbg
+ module purge
+ local _mlredir=0
+ '[' -n '' ']'
+ case " $@ " in
+ '[' 0 -eq 0 ']'
+ _module_raw purge
+ unset _mlshdbg
+ '[' 1 = 1 ']'
+ case "$-" in
+ set +x
+ unset _mlshdbg
+ return 0
+ module load gnu/11 mpi/openmpi/4 espresso/7.2.0
+ local _mlredir=0
+ '[' -n '' ']'
+ case " $@ " in
+ '[' 0 -eq 0 ']'
+ _module_raw load gnu/11 mpi/openmpi/4 espresso/7.2.0
+ unset _mlshdbg
+ '[' 1 = 1 ']'
+ case "$-" in
+ set +x
load module flavor/buildcompiler/gcc/11
load module flavor/gnu/standard
load module c++/gnu/11.2.0
load module c/gnu/11.2.0
load module fortran/gnu/11.2.0
load module gnu/11.2.0
load module flavor/buildmpi/openmpi/4
load module feature/openmpi/mpi_compiler/gcc
load module feature/mkl/single_node
load module feature/openmpi/io/standard
load module feature/openmpi/net/auto
load module flavor/ucx/cuda-11.6
load module flavor/cuda/nvhpc-222
load module cuda/11.6
load module flavor/libccc_user/hwloc2
load module hwloc/2.5.0
load module feature/hcoll/multicast/enable
load module sharp/2.4.2
load module hcoll/4.7.3191
load module ucx/1.18.1
load module pmix/4.2.2
load module mpi/openmpi/4.1.4
load module flavor/espresso/standard
load module flavor/fox/espresso
load module flavor/hdf5/parallel
load module flavor/fftw3/standard
load module fftw3/vanilla/3.3.9
load module fox/4.1.2
load module hdf5/1.12.0
load module blas/netlib/3.8.0
load module lapack/netlib/3.9.1
load module openblas/0.3.15
load module espresso/7.2.0
+ unset _mlshdbg
+ return 0
+ ccc_mprun -n 64 pw.x -npool 4 -i scf.in
+ ccc_mprun -n 64 pw.x -npool 4 -i nscf.in
+ ccc_mprun -n 16 pp.x -i pp.in
+ ccc_mprun -n 16 projwfc.x -i pdos.in
+ exit 0
