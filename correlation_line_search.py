import numpy as np
from astropy.io import fits

def correlation_func(spec,temp):
    m = len(spec)
    n = len(temp)
    sqrt_summed_tempsquare = np.sqrt(np.sum(temp**2))
    i  = 0
    corrdata=[]
    while(i+n<m):
        speccut = spec[i:i+n]
        corrdata.append(np.sum(speccut*temp)/(np.sqrt(np.sum(speccut**2))*sqrt_summed_tempsquare))
        i += 1
    ind = np.argmax(np.asarray(corrdata))
    return ind+n/2

'''
R2000
ind = ind - 11

R500_blue
ind = ind + 7

R500_red
ind = ind - 4
'''

def line_search(img,template,line_dist_from_template_centre):
    spec = np.sum(img,axis=0)
    temp = np.sum(template,axis=0)
    spec = spec/np.std(spec)
    ind = correlation_func(spec,temp)
    return ind + line_dist_from_template_centre