import numpy as np
import matplotlib.pyplot as plt
from astropy.io import ascii
import sys
from cube_generation import read_fits_images
import os

def closest(lst, K):
    lst = np.asarray(lst)
    idx = (np.abs(lst - K)).argmin()
    return idx

def science_and_lamp_data(path):
    spec_path=path+'Spectra/'
    if os.path.isdir(spec_path):
        scilist=os.listdir(spec_path)
        scilist=[os.path.join(spec_path,i) for i in scilist]
        science_data,timearr_science=read_fits_images(scilist)
    else:
        print('No science folder found. Check the path folder')
        stop
    lamp_path=path+'Lamp/'
    if os.path.isdir(lamp_path):
        lamplist=os.listdir(lamp_path)
        lamplist=[os.path.join(lamp_path,i) for i in lamplist]
        lamp_data,timearr_lamp=read_fits_images(lamplist)
    else:
        print('No lamp folder found. Check the path folder')
        stop
    ind=[closest(timearr_lamp,i) for i in timearr_science]
    return science_data,lamp_data[ind],timearr_science