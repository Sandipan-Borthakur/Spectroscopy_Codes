import numpy as np
from lmfit.models import LinearModel,GaussianModel

def closest(lst, K):
    lst = np.asarray(lst)
    idx = (np.abs(lst - K)).argmin()
    return idx

def Gaussian_fitting(x,yy):
    gmod = GaussianModel()
    pars = gmod.guess(yy, x=x)
    mod = gmod
    pars['center'].set(value = x[np.argmax(yy)])
    pars['sigma'].set(value = 5)
    pars['amplitude'].set(value = max(yy)-np.median(yy))
    pars['amplitude'].set(min = 0)
    out = mod.fit(yy, pars, x=x)

    param = [out.best_values['amplitude'],out.best_values['center'],out.best_values['sigma']]   #IDL first three parameter is [amp,cntr,sigma]
    return(out,param)

def Gaussian_plus_line_fitting(x,yy):
    cmod = LinearModel()
    gmod = GaussianModel()
    pars = gmod.guess(yy, x=x)             # Computer guess parameters for Gaussian
    mod = gmod + cmod                      # Model=Gaussian + Line
    slope=(int(yy[-1])-int(yy[0]))/(int(x[-1])-int(x[0]))
    pars.add('intercept', value=yy[0]-(slope*x[0]), vary=True)
    pars.add('slope', value=slope, vary=True)
    pars['center'].set(value = x[np.argmax(yy)])
    pars['sigma'].set(value = 1)
    pars['amplitude'].set(value = max(yy)-np.median(yy))
    pars['amplitude'].set(min = 0)
    out = mod.fit(yy, pars, x=x)

    param = [out.best_values['amplitude'],out.best_values['center'],out.best_values['sigma']]   #IDL first three parameter is [amp,cntr,sigma]
    return(out,param)