<p align="center">
  <img src="docs/images/logo.svg" alt="TcESTIME Logo" width="220"/>
</p>

# TcESTIME

Python code to estimate the critical temperature of hydrogen-based superconductors through the determination of its networking value.

TcESTIME is developed and maintained in the research group led by [Julia Contreras-García](https://www.lct.jussieu.fr/pagesperso/contrera/) at Sorbonne Université.

If you use TcESTIME, please cite: 
1. Novoa, T., di Mauro, M. E., Inostroza, D., El Haloui, K., Sisourat, N., Maday, Y., & Contreras-García, J. (2024). TcESTIME: predicting high-temperature hydrogen-based superconductors. [Chemical Science](https://pubs.rsc.org/en/content/articlelanding/2025/sc/d4sc04465g), 2025, 16, 57-68.

2. Belli, F., Novoa, T., Contreras-García, J., & Errea, I. (2021). Strong correlation between electronic bonding network and critical temperature in hydrogen-based superconductors. [Nature communications](https://www.nature.com/articles/s41467-021-25687-0), 2021, 12, 5381.

We welcome questions, comments and any kind of feedback, which is needed for the improvement of TcESTIME. Please direct them to [trinidadantonia.novoa@ehu.eus](mailto:trinidadantonia.novoa@ehu.eus).

## Dependencies

TcESTIME is developed in Python 3 and requires the following packages to operate:
- numpy
- scipy
- pandas
- matplotlib
- onnxruntime

## How to run TcESTIME?
Before running TcESTIME, make sure to set the PYTHONPATH to the folder containing the TcESTIME.py file. This can be done by

export PYTHONPATH=/path/to/TcESTIME

TcESTIME estimates the networking value of a system from the ELF and DOS. The input consists of a critic2 output file, containing information about the ELF critical points (as obtained with Quantum ESPRESSO, preferrably using PBE functional). If said file is located in /ex-dir/ex1.critic.out, TcESTIME is launched by

python3 TcESTIME.py /ex-dir/ex1.critic.out --opt OPT

The different command line options are:

-h, --help show this help message and exit
--hdos HDOS H_DOS value to be considered for T_c.
--dpdos DPDOS Directory where to find pdos files to get H_DOS (*.pdos*). Working dir is default.
--efermi EFERMI Fermi energy
--fit FIT Fit to estimate Tc ('leastsq', 'SR2', 'SR4', or 'GBR'). Default is 'leastsq'.
--odir ODIR Directory for output files.
--critic2 CRITIC2 Path to critic executable.
--plot PLOT Plot network of critical points. Default is False.

If HDOS is not specified, it can be computed by TcESTIME using the output of a QE calculation. For this, EFERMI must be specified, and the *.pdos.* files must be located in the DPDOS directory (that defaults to the working directory). If ODIR is not specified, all the output files are saved in the same directory as the input file. As for now, we recommend using absolute paths.

Possible fits for the estimation of Tc are:

'leastsq' : Linear fit between Tc and phi_dos = phi * h_f * (h_dos)^(1/3) obtained using least squares method. Tc^{leastsq} = 456.34 * phi * h_f * (h_dos)^(1/3) - 9.46

'SR2' : Symbolic regression fit (see https://doi.org/10.48550/arXiv.2403.07584, here phis is molecularity index) Tc^{SR2} = 442.3 * (1 - (phis - phi)) * h_f^3 * (h_dos)^(1/2)

'SR4' : Symbolic regression fit (see https://doi.org/10.48550/arXiv.2403.07584) Tc^{SR4} = 574.7 * phi * ( h_dos * h_f^3 )^(1/2)

'GBR' : Gradient Boosting regression fit (see https://doi.org/10.1039/D4SC04465G)

For the calculation of the critical points of the ELF using critic2, we recommend using the optimized parameters CPEPS 0.3 and NUCEPSH 0.6.

The output of TcESTIME is a standard output message containing the found networking value, molecularity index, H_DOS, H_f, and the critical temperature.

## TcESTIMEWeb
An online version of TcESTIME is available at [**TcESTIMEWeb**](https://lct-webtools.sorbonne-universite.fr/tcestime/), hosted at Sorbonne Université.  
It provides the same results and functionalities through a simple web interface.

## License

Tcestime works under a GNU license, please see the License file.

## Contributors
All contributors, in alphabetical order:
1. Nicolás F. Barrera
2. Carlos Cárdenas 
3. Julia Contreras-García
4. Trinidad Novoa
5. Ivon Maday
