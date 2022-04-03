import matplotlib.pyplot as plt
from tvsigma import tvsigmascl,contrast_control
import numpy as np
from correlation_line_search import line_search
from tools import closest, Gaussian_fitting, Gaussian_plus_line_fitting

def fit_function(prof,pixel_for_line,primary_half_width_pix,primary_pix_Threshold):
    if int(pixel_for_line) - primary_half_width_pix < 0:
        xmin=0
    else: xmin = int(pixel_for_line) - primary_half_width_pix

    if int(pixel_for_line) + primary_half_width_pix + 1 >1023:
        xmax = 1023
    else:
        xmax = int(pixel_for_line) + primary_half_width_pix + 1

    pixel_for_line = np.argmax(prof[xmin:xmax]) + xmin

    pix_array = np.arange(int(pixel_for_line) - primary_half_width_pix,
                          int(pixel_for_line) + primary_half_width_pix + 1)
    if pix_array.min()<0:
        pix_array=np.arange(0,int(pixel_for_line) + primary_half_width_pix + 1)
    if pix_array.max()>1023:
        pix_array = np.arange(int(pixel_for_line) - primary_half_width_pix,1023)
    count_array = prof[pix_array]
    fit, param = Gaussian_plus_line_fitting(pix_array, count_array)

    if abs(pixel_for_line - param[1]) > primary_pix_Threshold:
        print('Error in fitting!!')
        stop
    return param[1]


def auto_line_select(image):
    prof = np.sum(image,axis = 0)
    from scipy.signal import find_peaks
    peaks, _ = find_peaks(prof - np.median(prof), height=np.std(prof))
    disp_arr = (6717.04 - 6506.54) / (peaks[4:] - peaks[0:-4])
    index = np.argmin(abs(disp_arr - 1.15)) - 2

    return peaks[4:][index]

def calibration(image,template,line_dist_from_template_centre,dispersion,first_line_wavelength,primary_line_list,primary_half_width_pix,primary_pix_Threshold,primary_order,full_line_list,full_half_width_pix,full_pix_Threshold,continuum_list,fit_order_continuum,fit_order_calib):
    # global xpos,ypos
    ########################## Image Display and click on first line ###################################

    if dispersion < 1.0:
        xpos = auto_line_select(image)
    else:
        # (xpos,_) = contrast_control(image)
        xpos = line_search(image,template,line_dist_from_template_centre)

    ######################################### Plot profile ##############################################
    prof=np.sum(image,axis=0)

    xpos1 = np.argmax(prof[int(xpos) - 5:int(xpos) + 5]) + int(xpos) - 5

    ######################## Select range of profile and fit Gaussian+line ##############################

    first_pix_array=np.arange(int(xpos1)-5,int(xpos1)+5+1)
    first_count_array=prof[first_pix_array]

    fit,param=Gaussian_plus_line_fitting(first_pix_array,first_count_array)
    print(abs(xpos - param[1]))
    if abs(xpos-param[1])>primary_pix_Threshold:
        print('Error in fitting!')
        stop
    pix_to_wave=np.array([[param[1],first_line_wavelength]])

    ############################### Primary Wavelength Calibration #######################################
    ind = closest(primary_line_list, pix_to_wave[0, 1])
    i=0
    j,k=0,0
    while (j!=-99 or k!=-99):
        i = i + 1
        if ind+i<len(primary_line_list):
            if i==1:
                line=primary_line_list[ind+i]
                pixel_for_line=pix_to_wave[0,0]+(line-pix_to_wave[0,1])/dispersion
                if pixel_for_line <0 or pixel_for_line > 1023:
                    pass
                else:
                    param=fit_function(prof,pixel_for_line,primary_half_width_pix,primary_pix_Threshold)
                    pix_to_wave = np.concatenate((pix_to_wave, np.array([[param, line]])), axis=0)
            else:
                if len(pix_to_wave) == 2:
                    kind = 1
                elif len(pix_to_wave) == 3:
                    kind = 2
                else:
                    kind = 3
                line=primary_line_list[ind+i]
                q = np.polyfit(pix_to_wave[:, 1], pix_to_wave[:, 0], kind)
                func = np.poly1d(q)
                pixel_for_line=func(line)
                if pixel_for_line <0 or pixel_for_line >1023:
                    pass
                else:
                    param = fit_function(prof, pixel_for_line, primary_half_width_pix, primary_pix_Threshold)
                    pix_to_wave = np.concatenate((pix_to_wave, np.array([[param, line]])), axis=0)
        else:
            j=-99
        if ind-i>=0:
            if i==1:
                line = primary_line_list[ind - i]
                pixel_for_line = pix_to_wave[0, 0] + (line - pix_to_wave[0, 1]) / dispersion
                if pixel_for_line <0 or pixel_for_line > 1023:
                    pass
                else:
                    param = fit_function(prof, pixel_for_line, primary_half_width_pix, primary_pix_Threshold)
                    pix_to_wave = np.concatenate((pix_to_wave, np.array([[param, line]])), axis=0)
            else:
                if len(pix_to_wave) == 2:
                    kind = 1
                elif len(pix_to_wave) == 3:
                    kind = 2
                else:
                    kind = 3
                line=primary_line_list[ind-i]
                q = np.polyfit(pix_to_wave[:, 1], pix_to_wave[:, 0], kind)
                func = np.poly1d(q)
                pixel_for_line=func(line)
                if pixel_for_line <0 or pixel_for_line > 1023:
                    pass
                else:
                    param = fit_function(prof, pixel_for_line, primary_half_width_pix, primary_pix_Threshold)
                    pix_to_wave = np.concatenate((pix_to_wave, np.array([[param, line]])), axis=0)
        else:
            print('k', i, line)
            k=-99
        print(i, line, j, k)


    ####################################  Primary calibrated Wavelength ############################
    index = np.argsort(pix_to_wave[:, 0])
    pix_to_wave = pix_to_wave[index, :]

    primary_pixarr = np.arange(1024)
    q = np.polyfit(pix_to_wave[:, 0], pix_to_wave[:, 1], primary_order)
    p = np.poly1d(q)
    primary_wavearr = p(primary_pixarr)


    ##################################### Continuum polynomial and subtraction #####################
    continuum_wavelengths=continuum_list
    min=int(np.min(primary_wavearr))
    max=int(np.max(primary_wavearr))
    ind=np.where((continuum_wavelengths>=min) & (continuum_wavelengths<=max))[0]
    continuum_wavelengths=continuum_wavelengths[ind]
    ind=[closest(primary_wavearr,x) for x in continuum_wavelengths]
    continuum_wavelengths=primary_wavearr[ind]
    continuum_counts=prof[ind]

    q=np.polyfit(continuum_wavelengths,continuum_counts,fit_order_continuum)
    p=np.poly1d(q)
    primary_ccd_continuum=p(primary_wavearr)
    primary_bkg_sub_prof=prof-primary_ccd_continuum

    q=np.polyfit(pix_to_wave[:,1],pix_to_wave[:,0],4)
    func=np.poly1d(q)

    ##################################  Full List Calibration  #####################################
    primary_pix_to_new_wave=np.empty((0,2), float)
    for iline,line in enumerate(full_line_list):
        print(iline)
        line_pixel=int(func(line))
        if line_pixel <0 or line_pixel > 1023:
            pass
        else:
            if line_pixel - full_half_width_pix < 0:
                xmin = 0
            else:
                xmin = line_pixel - full_half_width_pix

            if line_pixel + full_half_width_pix + 1 > 1023:
                xmax = 1023
            else:
                xmax = line_pixel + full_half_width_pix + 1
            line_pixel = np.argmax(prof[int(xmin):int(xmax)]) + xmin
            primary_pixarr_crop = np.arange(int(xmin),int(xmax))
            primary_bkg_sub_prof_crop = primary_bkg_sub_prof[primary_pixarr_crop]
            fit,param=Gaussian_fitting(primary_pixarr_crop,primary_bkg_sub_prof_crop)
            if abs(line_pixel-param[1])<full_pix_Threshold:
                print(line_pixel-param[1])

                primary_pix_to_new_wave=np.concatenate((primary_pix_to_new_wave, np.array([[param[1],line]])), axis=0)

            primary_bkg_sub_prof[primary_pixarr_crop]=primary_bkg_sub_prof[primary_pixarr_crop]-fit.best_fit


    ####################### Polynomial fit and newly calibrated wavelength #########################
    q = np.polyfit(primary_pix_to_new_wave[:,0], primary_pix_to_new_wave[:,1],fit_order_calib)
    p = np.poly1d(q)
    new_wavearr=p(primary_pixarr)

    return(new_wavearr)