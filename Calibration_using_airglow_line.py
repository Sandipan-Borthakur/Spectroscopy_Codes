import matplotlib.pyplot as plt
import numpy as np
from lmfit import Model
import matplotlib
from draggable_lines import draggable_lines

def gaussian_fitting(x,amp,cen,wid):
    return amp * np.exp(-(x - cen) ** 2 / wid)

def key_press(event):
    global pressed_key,cond

    pressed_key = event.key
    if pressed_key in ['A', 'a']:
        plt.close()

def airglow_calibration(img, wavearr, los, lis, ris, ros, n_wave):

    bkg_flux = np.sum(img[los:lis, :], axis=0) + np.sum(img[ris:ros, :], axis=0)  # y values
    fig = plt.figure()
    ax = fig.add_subplot()

    wavearrlines = []
    for i in range(len(n_wave)):
        for j in range(-1, 3, 2):
            wavearrlines.append(draggable_lines(ax, n_wave[i] + j * 20, 'b', 10))
    ax.plot(wavearr,bkg_flux)
    if matplotlib.get_backend() == u'TkAgg':
        mng = plt.get_current_fig_manager()
        mng.window.state('zoomed')
    else:
        figManager = plt.get_current_fig_manager()
        figManager.window.showMaximized()
    thismanager = plt.get_current_fig_manager()
    thismanager.toolbar.zoom()
    plt.connect('key_press_event',key_press)
    plt.show()

    wavearrlines = [i.X for i in wavearrlines]
    wavearrmins = wavearrlines[::2]
    wavearrmaxs = wavearrlines[1::2]
    shifts = []
    model = Model(gaussian_fitting)
    for i in range(len(wavearrmins)):
        ind = np.where((wavearr >= wavearrmins[i]) & (wavearr <= wavearrmaxs[i]))[0]
        w = wavearr[ind]
        y = bkg_flux[ind]
        y_cont = (y[0] + y[-1]) / 2
        indpeak = np.argmax(y)
        params = model.make_params(cen=w[indpeak], amp=y[indpeak] - y_cont, wid=2)
        result = model.fit(y - y_cont, params, x=w)
        shifts.append(n_wave[i] - result.best_values['cen'])
    shift = np.mean(np.array(shifts))
    new_wavearr = wavearr + shift
    return new_wavearr