# laser_line_search2.py
# Work in progress -- testing method of searching residuals output by SpecMatch-Emp for laser lines
# Implemented based on David Lipman's description of his algorithm in his 2017 prject write-up.
# Last modified 8/13/20 by Anna Zuckerman


#import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import astropy.io.fits as pf
#from lmfit import Model
#from scipy.optimize import curve_fit
import math
from scipy.interpolate import interp1d
from mpmath import mp
mp.dps=100
exp_array = np.frompyfunc(mp.exp, 1, 1)

# function to insert simulated gaussians
def insert_gaussian(spectrum, gaussian_params, midpoint, numpoints):
    height = gaussian_params[0]
    position = gaussian_params[1] #position within segment, not index in spectrum
    FWHM = gaussian_params[2]
    offset = gaussian_params[3]
    x = np.linspace(0,numpoints-1,numpoints) # numpoints must be odd
    gauss = gaussian(x,height,position,FWHM/(2*np.sqrt(2*np.log(2))),offset)
    new_spect = spectrum
    new_spect[midpoint - math.floor(numpoints/2):midpoint + math.floor(numpoints/2)] = gauss
    return new_spect
    
def gaussian(x,a,b,c,d): # a = height, b = position of peak, c = width, x = numpy array of x values
    f = a*exp_array((-(x-b)**2)/(2*c)**2) + d
    return f 

#filenames = ['HIP101345_ragx_NDRR.fits', 'HIP10279_rbjg_NDRR.fits','HIP103096_rarc_NDRR.fits','HIP104202_raat_NDRR.fits','HIP104214_rapx_NDRR.fits','HIP104217_ragf_NDRR.fits','HIP105341_rbaw_NDRR.fits','HIP107350_rbmd_NDRR.fits','HIP108782_raba_NDRR.fits','HIP112774_rbgz_NDRR.fits' ]
#filenames = ['HIP10279_rbjg_NDRR.fits']
filenames = ['HIP101345_ragx_NDRR.fits']

all_hits = [None] * len(filenames)
all_idxs1 = [None] * len(filenames)
all_idxs2 = [None] * len(filenames)
all_idxs3 = [None] * len(filenames)
all_intensities = [None] * len(filenames)
i = 0
for filename in filenames:
    file = pf.open(filename)
    starname = filename.split('_')[0]
    spect = file[1].data # residual
    wl_all_regions = file[2].data # wl solution
    offset = 10
    spect = spect + offset # to avoid negative and zero values 
    
    median = np.median(spect)
    SD = np.std(spect)
    
    # To insert gaussians for signal injection and recovery purposes
    testing = False # False if not doing gaussian injection!
    if testing:
        gaussian_heights = np.linspace(0.1,1,10)
        gaussian_width = np.linspace(1,10,10)[9]
        gaussian_indxs = np.linspace(1000,48000,10).astype(int)
    #    count = 0
        for n in range(10):
            spect = insert_gaussian(spect,[gaussian_heights[n],49,int(gaussian_width),10], gaussian_indxs[n], 100)
#        count += 1
            
#    # To insert 100 gaussions in 1 residual
#    gaussian_heights = np.linspace(0.1,1,10)
#    gaussian_widths = np.linspace(1,15,10)
#    gaussian_indxs = np.linspace(1000,48000,100)
#    count = 0
#    for n in range(10):
#        for m in range (10):
#            spect = insert_gaussian(spect,[gaussian_heights[n],49,gaussian_widths[m],10], int(gaussian_indxs[count]), 100)
#            count += 1
#    spect = insert_gaussian(spect,[0.5,49,10,10], 10000, 100)
#    spect = insert_gaussian(spect,[0.5,49,5,10], 20000, 100)
#    spect = insert_gaussian(spect,[0.5,49,5,10], 30000, 100)
#    spect = insert_gaussian(spect,[0.5,49,2,10], 40000, 100)
    
    idxs_of_interest = []
    intensities = []
    idxs1 = []
    idxs2 = []
    idxs3 = []
    
    # laser line search
    peaks = []
    gaussians = []
    for idx in np.arange(len(spect))[100:-100]: #How to deal with ends that done't have 100 wide?
        #local_idxs_40 = np.arange(idx-20,idx+20)
        #local_values_40 = spect[local_idxs_40]
        local_median = median #np.median(spect) #local_values_40) 
        local_idxs_200 = np.arange(idx-100,idx+100)
        local_values_200 = spect[local_idxs_200]
        local_std = SD #np.std(local_values_200) 
        #if idx in gaussian_indxs:
        #    print('SD at gauss idx: ' + str(local_std))
        if all(np.greater(spect[idx-2:idx+2], 3*local_std + local_median)): # DL's writeup says mean here (?)
            idxs1 = idxs1 + [idx]
            if spect[idx] >= spect[idx-1] and spect[idx] >= spect[idx+1]: 
                if spect[idx] > spect[idx-2] and spect[idx] > spect[idx+2]:
                    idxs2 = idxs2 + [idx]
                    sample_pts = np.linspace(0,100,400)
                    interpolate = interp1d(np.linspace(0,100,100), spect[idx-50:idx+50])
                    interpolated_spect = interpolate(sample_pts)
                    idxs_values_within_noise = np.asarray(np.where(interpolated_spect < local_median + local_std))
                    try: 
                        left_idx = np.max(idxs_values_within_noise[idxs_values_within_noise < 200]) 
                        right_idx = np.min(idxs_values_within_noise[idxs_values_within_noise > 200])
                    except ValueError: # does not fall back below noise within 50 pixels
                        pass
                    height = spect[idx]
                    width = right_idx-left_idx
                    half_max = (spect[idx] - local_median)/2
                    # check how close to a gaussian the peak is
                    peak_interpd = interpolated_spect[left_idx:right_idx]
                    sample_points = np.linspace(0,width,width)
                    peaks = peaks + [peak_interpd]
                    idxs_interpd = np.asarray(np.where(peak_interpd > half_max + local_median)) 
                    idx_left_interpd = np.min(idxs_interpd)
                    idx_right_interpd = np.max(idxs_interpd)
                    FWHM_interpd = idx_right_interpd - idx_left_interpd
                    FWHM = FWHM_interpd/4
                    #print(FWHM_interpd)
                    # For true fitting to gaussian, use a variation of the lines below
                    #params, pcov = curve_fit(my_gaussian, x, peak, bounds=([.1,5,1],[.9,10,5]))
                    #gaussian = my_gaussian(np.linspace(0,width,width), params[0], params[1], params[2])
                    #gaussian = my_gaussian(x, height-10, idx, width) + 10 
                    #params, cov = curve_fit(gaussian, x, np.log(peak), bounds = (.01, 100)) # bounds so doesn't try ln(0))
                    #gaussian_fit = (gaussian(x, params[0], params[1], params[2], params[3]))
                    gaussian_fit = gaussian(sample_points, height-10, np.argmax(peak_interpd), FWHM_interpd/2.35, 10)
                    gaussians = gaussians + [gaussian_fit]
                    NRMSD = np.sqrt(np.sum((peak_interpd - gaussian_fit)**2)/len(peak_interpd))/(np.max(peak_interpd) - np.min(peak_interpd))
                    # For injection and recovery of gaussians
#                    if idx in gaussian_indxs-1:
#                        print('FWHM at ' + str(idx) + ' = ' + str(FWHM))
#                        print(NRMSD)
#                        plt.figure();plt.plot(peak_interpd,'k.-'); plt.plot(gaussian_fit,'g.-')
#                        #plt.axhline(local_median + 3*local_std)
#                        plt.ylabel('Normalized Intensity [arbitrary]')
#                        plt.xlabel('Pixels')
#                        plt.legend(['Injected gaussian'])#, 'Fit gaussian', '3*SD above median'])
                    if FWHM <= 10 and FWHM >= 3: # ??
                        idxs3 = idxs3 + [idx]
                        if NRMSD < 0.15:
                            idxs_of_interest = idxs_of_interest + [idx]
                            intensities = intensities + [(height - 10)/(local_std)] # how many times local std the peak is
                            print(str(idx) + ' / ' + str(wl_all_regions[idx]) + ' / ' + str(np.round(float(NRMSD),2)) + ' / ' + str(FWHM))
    
    #add to list of all hit idxs for all stars
    print(starname + ' ' + str(len(idxs_of_interest)), end = ': ')
    print(idxs_of_interest)
    all_hits[i] = idxs_of_interest
    all_idxs1[i] = idxs1
    all_idxs2[i] = idxs2
    all_idxs3[i] = idxs3
    all_intensities[i] = intensities
    print(i)
    i = i + 1
    
    # plot the peaks
    make_plots = True
    if make_plots:
        numplots = len(idxs_of_interest)
        wl_of_interest = wl_all_regions[idxs_of_interest]
        numfigs = math.ceil(numplots/10)
        numplots_remaining = numplots
        idxs_remaining = idxs_of_interest
        peaks_remaining = peaks
        gaussians_remaining = gaussians
        for figure in range(numfigs): # don't display more than 10 on same plot        
            fig = plt.figure()
            num = np.min([10,numplots_remaining])
            print('fig: ' + str(figure) + ', num: ' + str(num))
            for p in range(num):
                ax = plt.subplot(math.ceil(num/2), 2, p+1)
                ax.plot(peaks_remaining[p],'.-')
                #plt.plot(gaussians_remaining[p],'.-')
                plt.axhline(np.max(peaks_remaining[p]-median)/2 + median)
                #plt.axhline(median + SD)
                #plt.axhline(median + 3*SD, ls = '-')
                plt.legend(['peak: ' + str(round(wl_all_regions[idxs_remaining[p]],2)) + 'A'])
                #plt.legend(['peak ' + str(round(wl_all_regions[idxs_remaining[p]],2)) + 'A', 'gaussian'])
                #plt.title('peak at idx' + str(idxs_of_interest[p]))
                numplots_remaining = numplots_remaining - 1
                #print('    plot: ' + str(i))
            plt.suptitle(starname)
            if num == 10:
                peaks_remaining = peaks_remaining[10:]
                gaussians_remaining = gaussians_remaining[10:]
                idxs_remaining = idxs_remaining[10:]
    
        plt.figure();plt.plot(spect,'b.-')
        for idx in idxs_of_interest:
            plt.axvline(idx,color = 'k', linewidth = 2) 
#        for idx in gaussian_indxs-1:
#            plt.axvline(idx,color = 'r', linewidth = 1)
        plt.axhline(median + SD)
        plt.axhline(median + 3*SD, color = 'c', ls = '-')
        plt.title(starname)
        plt.legend(['Residual','Candidates'])#,'Injected gaussians'])
        plt.xlabel('Index in spectrum')
        plt.ylabel('Intensity')

        # for signal injection and recovery
        if testing:
            print('Gaussians caught in idxs1:')
            for idx in idxs1:
                if idx in gaussian_indxs-1:
                    print(str(idx) + ' ', end = '')
            print()
            print('Gaussians caught in idxs2:')
            for idx in idxs2:
                if idx in gaussian_indxs-1:
                    print(str(idx) + ' ', end = '')
            print()
            print('Gaussians caught in idxs3:')
            for idx in idxs3:
                if idx in gaussian_indxs-1:
                    print(str(idx) + ' ', end = '')                    
            print()
            print('Gaussians making it through:')
            for idx in idxs_of_interest:
                if idx in gaussian_indxs-1:
                    print(str(idx) + ' ', end = '')

# plot all hits
plot_hits = True
if plot_hits:
    plt.figure()
    all_hits = [x for x in all_hits if x is not None]
    all_intensities = [x for x in all_intensities if x is not None]
    for i in range(len(all_hits)):
        if not(all_hits[i]) == None:
            plt.plot(wl_all_regions[all_hits[i]], all_intensities[i],'.')
            plt.legend(filenames, fontsize = 10)
            plt.xlabel('Wavlength [A]')
            plt.ylabel('Intensity (# Standard Deviations)')
    plt.figure()
    flat_all_hits  = [val for sublist in all_hits for val in sublist]
    plt.hist(wl_all_regions[flat_all_hits], bins = np.arange(math.ceil(wl_all_regions[0]),math.ceil(wl_all_regions[-1]), 1))
    plt.xlabel('Wavelength, bins of 1 A')
    plt.ylabel('Number of hits')


    