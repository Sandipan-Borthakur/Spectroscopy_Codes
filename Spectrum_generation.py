import numpy as np
import matplotlib.pyplot as plt
import os
from astropy.io import ascii, fits
from astropy.table import Table
from deepCR.model import deepCR
from spectres import spectres
from Optical_long_slit_spec_reduction import slit_end_identification,estimate_aperture_sky_limits,sky_subtract
from Calibration import calibration
from Calibration_using_airglow_line import airglow_calibration
from Science_and_lamp_data_select import science_and_lamp_data

def spec_gen(path,objname,date_of_obs,resol,airglow_calib=True,savedata=True):

     if resol == 'R500_blue':
          dispersion = 3.7
          primary_half_width_pix = 8
          primary_pix_Threshold = primary_half_width_pix
          full_half_width_pix = 4
          full_pix_Threshold = 1
          first_line_wavelength = 7119.614
          fit_order_continuum = 4
          fit_order_calib = 3
          primary_order = 4
          line_dist_from_template_centre = 7
          n_wave = [5577.338]

     elif resol =='R500_red':
          dispersion = 3.7
          primary_half_width_pix = 8
          primary_pix_Threshold = primary_half_width_pix
          full_half_width_pix = 4
          full_pix_Threshold = 1
          first_line_wavelength = 9045.4415
          fit_order_continuum = 4
          fit_order_calib = 3
          primary_order = 4
          line_dist_from_template_centre = -4
          n_wave = [8344.602,8827.096]

     elif resol == 'R2000':
          dispersion = 1.1
          primary_half_width_pix = 8
          primary_pix_Threshold = primary_half_width_pix
          full_half_width_pix = 4
          full_pix_Threshold = 1
          first_line_wavelength = 6598.953
          fit_order_continuum = 4
          fit_order_calib = 3
          primary_order = 4
          line_dist_from_template_centre = -11
          n_wave = [5889.953, 5895.923, 6300.304]
     
     datafilepath = 'files_for_calibration/'
     instr_rspns_path = datafilepath + '2020116_InstrumentFunction_' + resol + '.dat'
     primary_line_list = ascii.read(datafilepath + 'primary_line_list_' + resol + '.csv')['Wavelength']
     full_line_list = ascii.read(datafilepath + 'full_line_list_' + resol + '.csv')['Wavelength']
     continuum_list = ascii.read(datafilepath + 'continuum_list_' + resol + '.csv')['Wavelength']
     template = fits.getdata(datafilepath + resol + '_pattern.fits')
     end_matching_template = datafilepath + resol + '_end_matching_template.txt'
     
     science_imgcube,lamp_imgcube,timearr = science_and_lamp_data(path)

     data = ascii.read(instr_rspns_path)
     sps_org_wave, ratio=data['col1'],data['col2']

     model = deepCR(mask='ACS-WFC-F606W-2-32', inpaint='ACS-WFC-F606W-2-32', device='CPU')

     for iimg in np.arange(science_imgcube.shape[0]):

          path1 = path+'aperture_info_{}.csv'.format(iimg)

          if os.path.isfile(path1):
               aperture=ascii.read(path1)
               le, los, lis, lap, rap, ris, ros, re = aperture['leftend'], aperture['los'],aperture['lis'],aperture['lap'],aperture['rap'],aperture['ris'],aperture['ros'], aperture['rightend']
               img = science_imgcube[iimg, int(le):int(re), :]
               _, img = model.clean(img, threshold=0.01, inpaint=True)

          else:
               img = science_imgcube[iimg,:,:]
               le,re,_ = end_search(img,end_matching_template)
               img = science_imgcube[iimg, le:re, :]
               _, img = model.clean(img, threshold=0.01, inpaint=True)
               los, lis, lap, rap, ris, ros = estimate_aperture_sky_limits(img, 'Sandipan')
               ascii.write([[le], [los], [lis], [lap], [rap], [ris], [ros], [re]],path1,names=['leftend', 'los','lis','lap','rap','ris','ros', 'rightend'],format='csv')

          los,lis,lap,rap,ris,ros=int(los),int(lis),int(lap),int(rap),int(ris),int(ros)
          spec_without_sky = sky_subtract(img,los, lis, lap, rap, ris, ros)
          spec = np.sum(spec_without_sky[:,0:spec_without_sky.shape[1]],axis=0)    # check once

          lap = lap + le
          rap = rap + le
          lamp_image = lamp_imgcube[iimg][int(lap):int(rap),:]
          science_wave = calibration(lamp_image,template,line_dist_from_template_centre,dispersion,first_line_wavelength,primary_line_list,primary_half_width_pix,primary_pix_Threshold,primary_order,full_line_list,full_half_width_pix,full_pix_Threshold,continuum_list,fit_order_continuum,fit_order_calib)
          if airglow_calib:
               science_wave=airglow_calibration(img,science_wave,los, lis, ris, ros,n_wave)

          min=np.min(sps_org_wave)
          max=np.max(sps_org_wave)
          index=np.where((science_wave>=min) & (science_wave<=max))[0]
          science_corr_spec = spec[index]/spectres(science_wave[index], sps_org_wave, ratio)

          wavelength = science_wave[index]
          flux = science_corr_spec
          plt.plot(wavelength,flux,'b')
          plt.show()
          t = Table([wavelength,flux], names=('Wavelength', 'Counts'))
          if savedata:
               ascii.write(t, path+objname+'_spec_'+resol+'_'+date_of_obs+'_{}.dat'.format(timearr[iimg]), format='csv')
