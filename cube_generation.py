import numpy as np
import astropy
from astropy.io import fits
from astropy.time import Time
import os
import glob
#from deepCR.model import deepCR

def read_fits_images(filelist):
    nimg = 0
#    model = deepCR(mask='ACS-WFC-F606W-2-32', inpaint='ACS-WFC-F606W-2-32', device='CPU')

    for filename in filelist:
        header = fits.getheader(filename)
        nimg += header['NAXIS3']
    
    imgcube = np.zeros((nimg, header['NAXIS2'], header['NAXIS1']))
    timeArr = np.zeros(nimg)
    count = 0
    for filename in filelist:
        header = fits.getheader(filename)
        tempn = header['NAXIS3']
        imgcube[count:count + tempn, :, :] = fits.getdata(filename)
        
        t = Time(header['FRAME'], format='isot', scale='utc')  # Time will be in IST
        t_exposure_begin = (t.jd - (5.5 / 24.0))  # to convert from IST to UT
        print(t_exposure_begin)
        t_frame = t_exposure_begin + header['EXPOSURE'] / (2*24.0 * 3600.0)  # Time of mid-exposure
        print(t_frame)
        timeArr[count:count + tempn] = t_frame + (np.arange(tempn) * header['KCT']) / (
                24.0 * 3600.0)  # time array of mid-exposure of each frames
        count += tempn
    return imgcube, timeArr

def gen_bias(data_path):
    biasfolder = os.path.join(data_path, 'bias')
    biaslist = sorted(glob.glob(os.path.join(biasfolder, '*.fits')))
    biasCube,_ = read_fits_images(biaslist)
    masterBias = np.median(biasCube, axis=0)

    return masterBias


def gen_flat(data_path, selected_filter, masterBias):
    flatfolder = os.path.join(data_path, 'flat')
    flatlist = sorted(glob.glob(os.path.join(flatfolder, '*.fits')))

    flat_spec_filter = []
    for f in flatlist:
        temp = [x.lower() for x in f.split(".")[0].split("_")]
        if selected_filter.lower() in temp:
            flat_spec_filter.append(f)

    flatCube,_ = read_fits_images(flat_spec_filter)
    
    for ii in range(flatCube.shape[0]):
        flatCube[ii,:,:] -= masterBias
        normfactor = np.median(flatCube[ii,:,:])
        flatCube[ii, :, :] /=  normfactor

    masterFlat = np.median(flatCube, axis=0)

    if np.any(masterFlat < 0.2):
        masterFlat[masterFlat < 0.2] = float('NaN')     # Set all flat-field values lower than 0.2 to NaN

    return  masterFlat


def gen_img_cube(data_path, sciencelist, masterBias, masterFlat):
    sciencefolder = os.path.join(data_path, 'science')
    for i in range(len(sciencelist)):
        sciencelist [i] = os.path.join(sciencefolder, sciencelist[i])
    scienceCube, timeArr = read_fits_images(sciencelist)
    
    # for ii in range(scienceCube.shape[0]):
    #     scienceCube[ii, :, :] -= masterBias
    #     scienceCube[ii, :, :] /= masterFlat

    return scienceCube, timeArr

def cube_gen(data_path, onlyfile_spec_filter, selected_filter):
    
    masterBias = gen_bias(data_path)

    masterFlat = gen_flat(data_path, selected_filter, masterBias)

    imgCube, timeArr = gen_img_cube(data_path, onlyfile_spec_filter, masterBias, masterFlat)

    return imgCube, timeArr