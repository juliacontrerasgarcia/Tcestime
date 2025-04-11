
# TcESTIME
Please cite us: xxxxx
Tcestime works under a GNU license

Software to estimate the critical temperature of a superconductor through the determination of its networking value.

Developed by Trinidad Novoa, J. Contreras-García and Yvon Maday.

If you use TcESTIME, please cite:
Novoa, T., di Mauro, M. E., Inostroza, D., El Haloui, K., Sisourat, N., Maday, Y., & Contreras-García, J. (2024). TcESTIME: predicting high-temperature hydrogen-based superconductors. Chemical Science.

Belli, F., Novoa, T., Contreras-García, J., & Errea, I. (2021). Strong correlation between electronic bonding network and critical temperature in hydrogen-based superconductors. Nature communications, 12(1), 5381.

We welcome questions, comments and any kind of feedback, which is needed for the improvement of TcESTIME. Please direct them to trinidadantonia.novoa@ehu.eus.


#  Dependencies 

TcESTIME is written in Python3, and needs the following packages to function:

* numpy
* matplotlib
* pandas
* pickle
* scikit-learn==1.4.1 (other versions might fail for GBR method)


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
  --fit FIT          Fit to estimate Tc ('leastsq', 'SR2', 'SR4', or 'GBR'). Default is 'leastsq'.
  --odir ODIR        Directory for output files.
  --critic2 CRITIC2  Path to critic executable.
  --plot PLOT        Plot network of critical points. Default is False.


If HDOS is not specified, it can be computed by TcESTIME using the output of a QE calculation. For this, EFERMI must be specified, and the \*.pdos.\* files must be located in the DPDOS directory (that defaults to the working directory). 
If ODIR is not specified, all the output files are saved in the same directory as the input file. As for now, we recommend using absolute paths. 

Possible fits for the estimation of Tc are:

* 'leastsq' : Linear fit between Tc and phi_dos = phi * h_f * (h_dos)^(1/3) obtained using least squares method.
Tc^{leastsq} = 456.34 * phi * h_f * (h_dos)^(1/3) - 9.46

* 'SR2' : Symbolic regression fit (see https://doi.org/10.48550/arXiv.2403.07584, here phis is molecularity index)
Tc^{SR2} = 442.3 * (1 - (phis - phi)) * h_f^3 * (h_dos)^(1/2)

* 'SR4' : Symbolic regression fit (see https://doi.org/10.48550/arXiv.2403.07584)
Tc^{SR4} = 574.7 * phi * ( h_dos * h_f^3 )^(1/2)

* 'GBR' : Gradient Boosting regression fit (see xxxxxxxx)


For the calculation of the critical points of the ELF using critic2, we recommend using the optimized parameters CPEPS 0.3 and NUCEPSH 0.6.

The output of TcESTIME is a standard output message containing the found networking value, molecularity index, H_DOS, H_f, and the critical temperature.
