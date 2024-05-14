
# TcESTIME
Please cite us: xxxxx
Tcestime works under a GNU license

Software to estimate the critical temperature of a superconductor through the determination of its networking value.

Developed by Trinidad Novoa, J. Contreras-García and Yvon Maday.

For more information see: https://doi.org/10.1038/s41467-021-25687-0

We welcome questions, comments and any kind of feedback, which is needed for the improvement of TcESTIME. Please direct them to trinidad.novoa_aguirre@sorbonne-universite.fr.


#  Dependencies 

TcESTIME is written in Python3, and needs the following packages to function:

* numpy
* matplotlib
* pandas


#  Run TcESTIME  

Before running TcESTIME, make sure to set the PYTHONPATH to the folder containing the TcESTIME.py file.

TcESTIME estimates the networking value of a system from the ELF and DOS. The input consists of a critic2 output file (stable version), containing information about the ELF critical points (as obtained with QE or VASP). If said file is located in /ex-dir/ex1.critic.out, TcESTIME is launched by

python3 TcESTIME.py /ex-dir/ex1.critic.out --opt OPT

The different command line options are:
  -h, --help         show this help message and exit
  --hdos HDOS        H_DOS value to be considered for T_c.
  --dpdos DPDOS      Directory where to find pdos files to get H_DOS (\*.pdos\*). Working dir is
                     default.
  --efermi EFERMI    Fermi energy
  --fit FIT          Fit to estimate Tc ('meansq', 'SR2', or 'SR4'). Default is 'meansq'.
  --odir ODIR        Directory for output files.
  --critic2 CRITIC2  Path to critic executable.
  --plot PLOT        Plot network of critical points. Default is False.


If HDOS is not specified, it can be computed by TcESTIME using the output of a QE calculation. For this, EFERMI must be specified, and the \*.pdos.\* files must be located in the DPDOS directory (that defaults to the working directory). 
If ODIR is not specified, all the output files are saved in the same directory as the input file. As for now, we recommend using absolute paths. 

It is also possible to provide a cube file of the ELF, and run critic2 directly within TcESTIME. In this case, critic2 must be already installed in the system. The calculations will be performed using the optimized parameters CPEPS 0.3 and NUCEPSH 0.6. TcESTIME recognizes the cube input file by its extension. Then, the program is launched by

python3 TcESTIME.py /ex-dir/ex1.cube --opt OPT

The output of TcESTIME is a standard output message containing the found networking value, molecularity index, H_DOS, H_f, and the critical temperature.
