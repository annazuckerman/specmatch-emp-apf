# specmatch-emp-apf
Summer 2020 Breakthrough Listen Internship project.

This verions of specmatch-emp uses Cameron Nunez's modifications and additions (stevecroft/bl-interns/cameronn) to Samuel Yee's (samuelyeewl/specmatch-emp) Specmatch-Emp model.
Cameron's modifications allowed the model to read in APF spectra instead of Keck HIRES spectra.
New modifications in this version include use of Jackie Telson's (stevecroft/bl-interns/jackietel) deblazing function written in python instead of the original R deblazing function, modification to allow the script to run on a directory containing spectra of mulitple stars (and output results for each star), slight changes to allow the model to work in my python environment (for example, python verion compatibility issues).

See project write-up for further details about the scripts, data, methods, and (preliminary) results of this project

To run, use smemp_multifile.ipynb. Note that unless otherwise stated, all 'spectra' are assumed to be in the format of APF fits files. 

### Contents of This Repository:

README.md

#### Specmatch_scripts -> *scripts and files neccessary to run model on its own*

  smemp_multifile.ipynb  -> *script to run Specmatch on a directory containing APF spectra of multiple stars*
  
  specmatchemp -> the scripts needed to run Specmatch-emp, which are called by smemp_multifile and smemp_apf_test (ADD THIS)
  
  bstar_deblaze.ipynb  -> *deblaze target spectrum*
  
  rescale.ipynb -> *rescale spectrum*
  
  apf_wave copy.fits  -> *file containing wavelength solutions used by Specmatch*
  
#### Data 

  apf_spectra -> *spectra of stars that both have APF spectra and were analyzed by Yee et al. 2017*
  
  apf_spectra_highest_SNR -> *apf_spectra grouped such that only the highest SNR set of observations is used for each star*

#### Calibration

  validate_smemp.ipynb -> *script to compare APF Specmatch results using to published values from Yee et al.*
  
  yee_library_full.csv -> *properties for Yee et al. catalog stars*
  
#### Supporting Files

  smemp_apf_test.ipynb -> *run Specmatch on a single spectrum (or directory of multiple spectra for single star)*

  all_apf_non_i2.csv -> *file containing list of all APF spectra files and corresponding star names*

  apf_name_conversion.csv -> *file containig filename, name in all_apf_non_i2, and HIP name of APF stars*
  
  calc_SNR.ipynb -> *calculate the signal-to-noise ratio for single fits spectrum or directory of spectra of single star*
  
  check_file_labeling.ipynb -> *check naming conventions within spectra files or that each file in a directory is for the same star*
  
  get_all_norm_deblazed.ipynb -> *get normalized, deblazed spectra for input spectra*
  
  group_by_SNR.ipynb -> *with set of files grouped by star (as by group_spectra.ipynb), saves new directory of highest SNR set for each*
  
  group_spectra.ipynb -> *groups spectra file such that if mulitple files per star, creates directory and groups those files*
  
  smemp_keck_and_apf.ipynb -> *NOTE YET WORKING script to run Specmatch on either Keck or APF spectra*
  
NOTE: The current scripts need to be updated!
