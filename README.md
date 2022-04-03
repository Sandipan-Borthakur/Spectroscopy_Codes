# Spectroscopy_Codes
 Reduce spectroscopy data from MFOSC-P instrument mounted on Mt. Abu 1.2m telescope

To run the code, use spec_gen function in Spectrum_generation. 
To test the code, use the data present in R500_blue folder and use Spectroscopy.py to run.

spec_gen(path,objname,date_of_obs,resol,airglow_calib=True,savedata=True,**ends)

path = path of the data folder. The folder should contain two sub-folders - "Lamp" and "Spectra". For eg. for R500_blue folder data
           provide path = 'R500_blue'
objname = Name of the object
date_of_obs = Observation Date
resol = Resolution used. Options are - R500_blue, R500_red, R2000
airglow_calib = For refined wavelength calibration using airglow lines. Default value is True.
savedata = Save the wavelength and spectra in one file in the same path as the data folder.
**end = The slit ends. Provide this value if the code is run first time for the data folder used.

Returns : None.

Dependencies - 
1. deepCR (pip install deepCR) 

Steps to follow - 
After the code is run, a plot will appear with three subplots. These plots are to select the aperture for sky and star. You can use
any of the subplots to select the aperture.
1. 7 lines will appear in the plot. The black line is for reference.
2. Two green lines will appear on either side of the black line. Press "g" and click the lines to select the aperture for the star light.
3. Two orange lines will appear on either side of the black line. Press "o" and click the position where you wan to move the line. 
    To select the inner aperture for the sky
     background.
4. Two red lines will appear on either side of the black line. Press "r" and click to the location you want to move the line. 
     To select the outer aperture for the sky background.
5. press "a" for the code to accept the position of these lines.
6. If airglow_calib = True, then two lines will appear for each airglow lines chosen within the program. Drag those lines such that it 
    bounds the airglow line. 
7. Press "a" for the code to accept.
