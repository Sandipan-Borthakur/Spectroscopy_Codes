import numpy as np
from scipy.signal import savgol_filter
from correlation_line_search import correlation_func

def end_search(img,templatepath):
    template = np.loadtxt(templatepath)
    img = np.sum(img,axis=1)
    n = int(len(template))
    y = savgol_filter(img,5,1)
    y = y[1:]-y[:-1]
    ind = int(correlation_func(y,template)) - int(n/2)
    ymaxleft = np.argmax(y[:ind]) + 2
    yminright = np.argmin(y[ind+n:]) + ind+n - 2
    ypeak = np.argmax(img[ymaxleft:yminright]) + ymaxleft
    return ymaxleft,yminright,ypeak
