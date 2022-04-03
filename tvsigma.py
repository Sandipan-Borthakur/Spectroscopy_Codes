import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider
import matplotlib

def onclick(event):
    global xpos,ypos
    if event.button==3:
        xpos=event.xdata
        ypos=event.ydata
        plt.close()

def contrast_control(img, f1=1, f2=1,click=True,cmap='gray',interpolation='None'):         #Image scaling function
    fig, ax = plt.subplots()
    plt.subplots_adjust(bottom=0.35)
    plt.imshow(img, vmin=np.median(img) - f1 * np.std(img), vmax=np.median(img) + f2 * np.std(img), cmap=cmap,
               origin='lower')
    axf1 = plt.axes([0.25, 0.2, 0.65, 0.03])
    axf2 = plt.axes([0.25, 0.15, 0.65, 0.03])
    f1slider = Slider(axf1, 'f1', 0.0, 1.0, 1.)
    f2slider = Slider(axf2, 'f2', 0.0, 1.0, 1.)

    def update(val):
        f1 = f1slider.val
        f2 = f2slider.val
        ax.imshow(img, vmin=np.median(img) - f1 * np.std(img), vmax=np.median(img) + f2 * np.std(img), cmap=cmap,
                  origin='lower',interpolation=interpolation)

    f2slider.on_changed(update)
    f1slider.on_changed(update)
    if matplotlib.get_backend() == u'TkAgg':
        mng = plt.get_current_fig_manager()
        mng.window.state('zoomed')
    else:
        figManager = plt.get_current_fig_manager()
        figManager.window.showMaximized()
    thismanager = plt.get_current_fig_manager()
    thismanager.toolbar.zoom()

    if click:
        plt.connect('button_press_event', onclick)
    plt.show()
    return xpos,ypos



def tvsigmascl(img, factor1=1, factor2=1):         #Image scaling function
    med = np.median(img)
    std = np.std(img)
    img1 = img.copy()
    ind = np.where(img < med-std*factor1)
    img1[ind] = med-std*factor1
    ind = np.where(img > med+std*factor2)
    img1[ind] = med+std*factor2
    return img1
