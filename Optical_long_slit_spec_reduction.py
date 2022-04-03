import matplotlib.pyplot as plt
import numpy as np
import os
import matplotlib
from cube_generation import read_fits_images
from tvsigma import tvsigmascl
from lmfit.models import LinearModel,GaussianModel
import matplotlib.gridspec as gridspec
from tools import closest, Gaussian_fitting, Gaussian_plus_line_fitting

################################ Two Click function ###############################
def twoclick(event):
    global xpos1,ypos1,xpos2,ypos2

    if event.button==3:
        if xpos1 == -1:                   # to be defined as xpos1=-1 wherever this func is called
            xpos1=event.xdata
            ypos1=event.ydata
        else:
            xpos2=event.xdata
            ypos2=event.ydata
            plt.close()


##############################  Idenitfy the slit ends by clicking from viewer ##########################################

def slit_end_identification(science_imgcube, calib_path):
    global xpos1, ypos1, xpos2, ypos2
    caliblist = os.listdir(calib_path)                         # List of files in calibration folder to be used
    for ifile, filename in enumerate(caliblist):
        caliblist[ifile] = os.path.join(calib_path, filename)

    calib_imgcube,_ = read_fits_images(caliblist)


    data1 = np.sum(calib_imgcube, axis=0)
    data2 = np.sum(science_imgcube, axis=0)

    data = data1 + data2

    xpos1 = -1
    plt.plot(np.mean(data,axis=1))
    plt.connect('button_press_event',twoclick)
    plt.show()

    leftend = int(np.ceil(np.min([xpos1, xpos2])))        # leftend and rightend are the slit ends to be given by the
    rightend = int(np.floor(max([xpos1, xpos2])))         # user by clicking on the image( 5th line upwards from here)

    return leftend, rightend


#################### Subtract sky from the image using apertures from aperture_sky_limits function ###################

def sky_subtract(img,los, lis, lap, rap, ris, ros):
    global meansky
    leftsky=np.median(img[los:lis,:],axis=0)
    rightsky=np.median(img[ris:ros,:],axis=0)
    meansky=(leftsky+rightsky)/2.0
    spec_without_sky=np.subtract(img[lap:rap,:],meansky)
    return spec_without_sky


def key_press_accept(event):
    global cond_stop, sil, sol, sir, sor, pl, pr, new_cntr, pressed_key
    pressed_key = event.key

    if pressed_key in ['A', 'a']:
        print(pressed_key)
        cond_stop = 1
        plt.close()


def drag_line(event):
    global cond_stop, sil, sol, sir, sor, pl, pr, new_cntr, pressed_key, xclick
    if event.button == 3:  # For Right click
        cond_stop = 0
        xclick = int(round(event.xdata))

        if pressed_key in ['R', 'r']:  # 'R' for red lines
            print(pressed_key)
            plt.close()
            ################## For red line ################
            if xclick < (new_cntr): sol = xclick
            if xclick > (new_cntr): sor = xclick

            if sil < sol: sol = sil - 2
            if sir > sor: sor = sir + 2
            ################################################
            print(sol, sor)

        if pressed_key in ['O', 'o']:  # 'O' for orange lines
            plt.close()
            ################## For orange line ################
            if xclick < (new_cntr): sil = xclick
            if xclick > (new_cntr): sir = xclick

            if sil < sol: sil = sol + 2
            if sir > sor: sir = sor - 2
            ################################################

        if pressed_key in ['G', 'g']:  # 'O' for orange lines
            print(pressed_key)
            plt.close()
            ################## For orange line ################
            if xclick < (new_cntr): pl = xclick
            if xclick > (new_cntr): pr = xclick


def estimate_aperture_sky_limits(img, filename):
    global cond_stop, sil, sol, sir, sor, pl, pr, new_cntr, pressed_key, xclick, setx
    prof = np.sum(img, axis=1)
    xprof = np.arange(len(prof))
    fit, param = Gaussian_plus_line_fitting(xprof, prof)

    minprof = min(prof)
    maxprof = max(prof)

    fwhm = param[2] * 2.355
    xlines = [param[1] - fwhm * 6, param[1] - fwhm * 5, param[1] - fwhm * 3, param[1] + fwhm * 3, param[1] + fwhm * 5,
              param[1] + fwhm * 6]

    # color=['red', 'orange', 'green', 'green', 'orange', 'red']
    xlines = np.sort(xlines)
    sol = int(xlines[0])
    sil = int(xlines[1])
    pl = int(xlines[2])
    pr = int(xlines[3])
    sir = int(xlines[4])
    sor = int(xlines[5])

    if sol < 0: sol = 0
    if sil <= sol: sil=int(sol+fwhm)
    if sor >= len(prof): sor = len(prof)-1

    if sil< 0: sil = int(fwhm)
    if sir >= sor: sir=int(sor-fwhm)


    ############################## Linear background fitting ################################
    x1 = np.arange(sil - sol + 1) + sol
    x2 = np.arange(sor - sir + 1) + sir
    xx = np.concatenate((x1, x2))
    xbg = np.arange(sor - sol + 1) + sol
    y1 = prof[sol:(sil + 1)]
    y2 = prof[sir:(sor + 1)]
    y = np.concatenate((y1, y2))
    std = np.std(y)  # Need to concatenate elements in order to find standard deviation and median
    med = np.median(y)
    z = np.polyfit(xx, y, 1)
    p = np.poly1d(z)
    ybg = p(xbg)
    ##############################################################################

    cond_stop = 0
    xclick = -1
    while cond_stop == 0:
        if xclick != -1:
            ############################## Linear background fitting ################################
            x1 = np.arange(sil - sol + 1) + sol
            x2 = np.arange(sor - sir + 1) + sir
            xx = np.concatenate((x1, x2))
            xbg = np.arange(sor - sol + 1) + sol
            y1 = prof[sol:(sil + 1)]
            y2 = prof[sir:(sor + 1)]
            y = np.concatenate((y1, y2))
            std = np.std(y)  # Need to concatenate elements in order to find standard deviation and median
            med = np.median(y)
            z = np.polyfit(xx, y, 1)
            p = np.poly1d(z)
            ybg = p(xbg)
            ##############################################################################

        new_cntr = param[1]  # hardcoded. Very appropriate and robust. New_cntr calculated through gaussian may not be correct in case of faint spectrum contaminated by bright spectrum of nearby source.
        fig = plt.figure(filename)

        gs = gridspec.GridSpec(2, 3)
        gs.update(left=0.05, right=0.99, wspace=0.1, hspace=0.1)
        ax = plt.subplot(gs[1, :2])
        ax.plot(prof)  # Use color='white' to change the color of plot
        ax.plot([sil, sil], [minprof, maxprof], 'orange')
        ax.plot([sir, sir], [minprof, maxprof], 'orange')
        ax.plot([sol, sol], [minprof, maxprof], 'red')
        ax.plot([sor, sor], [minprof, maxprof], 'red')
        ax.plot([pl, pl], [minprof, maxprof], 'green')
        ax.plot([pr, pr], [minprof, maxprof], 'green')
        ax.plot([new_cntr, new_cntr], [minprof, maxprof], 'k')
        ax.plot(xbg, ybg, color='#CCCC00')

        ax1 = plt.subplot(gs[0, :2])
        ax1.plot(prof)
        ax1.set_ylim([med - 4 * std, med + 4 * std])
        ax1.plot([sil, sil], [minprof, maxprof], 'orange')
        ax1.plot([sir, sir], [minprof, maxprof], 'orange')
        ax1.plot([sol, sol], [minprof, maxprof], 'red')
        ax1.plot([sor, sor], [minprof, maxprof], 'red')
        ax1.plot([pl, pl], [minprof, maxprof], 'green')
        ax1.plot([pr, pr], [minprof, maxprof], 'green')
        ax1.plot([new_cntr, new_cntr], [minprof, maxprof], 'k')
        ax1.plot(xbg, ybg, color='#CCCC00')

        ax2 = plt.subplot(gs[:2, 2])
        imglen = img.shape[1] - 1  # It gives 1024-1=1023
        ax2.plot([sil, sil], [0, imglen], 'orange')
        ax2.plot([sir, sir], [0, imglen], 'orange')
        ax2.plot([sol, sol], [0, imglen], 'red')
        ax2.plot([sor, sor], [0, imglen], 'red')
        ax2.plot([pl, pl], [0, imglen], 'green')
        ax2.plot([pr, pr], [0, imglen], 'green')
        ax2.plot([new_cntr, new_cntr], [0, imglen], 'k')
        ax2.imshow(tvsigmascl(np.transpose(img)), origin='lower', cmap='gray', interpolation='none')

        plt.connect('button_release_event', drag_line)
        plt.connect('key_press_event', key_press_accept)
        manager = plt.get_current_fig_manager()
        manager.toolbar.zoom()
        if matplotlib.get_backend() == u'TkAgg':
            mng = plt.get_current_fig_manager()
            mng.window.state('zoomed')  # works fine on Windows!
        else:
            figManager = plt.get_current_fig_manager()
            figManager.window.showMaximized()
        plt.pause(0.001)
        plt.show(block=True)

    #######################################################################################
    return sol, sil, pl, pr, sir, sor



