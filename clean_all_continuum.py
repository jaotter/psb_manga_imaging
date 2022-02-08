# coding: utf-8

import os
import csv
        


plifu_list = []
chan_lower = []
chan_upper = []
radius_list = []
with open('listobs_params.csv', mode='r') as fl:
    params = csv.reader(fl)
    for i, lines in enumerate(params):
        if i == 0:
            continue
        else:
            plifu_list.append(lines[0])
            chan_upper.append(lines[-3])
            chan_lower.append(lines[-2])
            radius_list.append(lines[-1])

#CO rest freq
restfreq = "115.271202GHz"

theoutframe = 'LSRK'
theveltype = 'radio'

restoringbeam = ['2.5arcsec']
restoringbeam = 'common'

niter = 100000
robust_value = 0.5
thecellsize = '0.5arcsec'
theimsize=[256,256]

import_pipe3d = False

print(plifu_list)


for ind, plateifu in enumerate(plifu_list): #skipping first bc I tested w that galaxy
    if plateifu == '8655-3701':
        continue
    if ind < 7:
        continue

    print('BEGINNING IMAGING FOR '+plateifu)
    datadir = '/lustre/cv/observers/cv-12578/data/'
    savedir = datadir+'data_products/target'+plateifu+'/cont_imaging/'
    fitsdir = datadir+'data_products/fitsimages/'
    msdir = datadir+'split_ms/'
    pipe3ddir = datadir+'pipe3d/'

    if not os.path.isdir(savedir):
        os.mkdir(savedir)
    os.chdir(datadir)
    
    fullvis = msdir+'target'+plateifu+'_vis.ms'
    if plateifu == '8081-3702' or plateifu == '9088-9102' or plateifu == '9494-3701':
        fullvis = msdir+'target'+plateifu+'_concat_vis.ms'

    spwrange = '1,2,3,0:0~'+chan_lower[ind]+';'+chan_upper[ind]+'~1920'
    #spwrange= '1,2,3'

    xpos=str(theimsize[0]/2)
    ypos=str(theimsize[1]/2)
    radius = str(radius_list[ind])
    cleanmask = 'circle[['+xpos+'pix,'+ypos+'pix], '+radius+'pix]'

    imgname = 'target'+plateifu+'_cont_spw0123_r'+str(robust_value)+'_mask'#+'_exchans:'+lower_chan+'-'+upper_chan
    d_imgname = imgname+'.dirty'

    #creating dirty cube
    tclean(vis=fullvis,
           imagename=savedir+d_imgname,
           field=plateifu,
           spw=spwrange,
           restfreq=restfreq,
           threshold='1Jy', # high threshold for dirty cube  
           imsize=theimsize,  # we used [256,256], just to make sure there is no weird features outside of the galaxy
           cell=thecellsize,
           outframe=theoutframe,
           restoringbeam=restoringbeam,  # to match MaNGA resolution,  # “common” will give you the native beam size of this observation, use restoringbeam=[’2.5arcsec’] to generate a map with resolution similar to that of MaNGA. 
           specmode='mfs',
           gridder='standard',
           veltype=theveltype,
           niter=0, # 0 for dirty cube 
           pbcor=False,
           deconvolver='hogbom',
           weighting = 'briggs', #'briggs' or 'natural' or 'uniform' 
           robust = robust_value,
           mask = cleanmask,
           interactive=False)

    exportfits(imagename=savedir+d_imgname+'.image',
               fitsimage=fitsdir+d_imgname+'.fits',
               overwrite=True)
    
    imstats = imstat(savedir+d_imgname+'.image')
    imgrms = imstats['rms'][0]
    str_rms = str(round(imgrms, 5))
    c_imgname = imgname+'_'+str_rms+'Jy'
    
    tclean(vis=fullvis,
           imagename=savedir+c_imgname,
           field=plateifu,
           spw=spwrange,
           restfreq=restfreq,
           threshold=str(imgrms)+'Jy', # rms of cube, we clean down to 1sigma 
           imsize=theimsize,  # we used [256,256], just to make sure there is no weird features outside of the galaxy
           cell=thecellsize,
           outframe=theoutframe,
           restoringbeam=restoringbeam,                                                                               
           specmode='mfs',
           gridder='standard',
           veltype=theveltype,
           niter=niter, # we use 2000 or so, a large number anyway.
           pbcor=False,
           deconvolver='hogbom',
           weighting = 'briggs', #'briggs' or 'natural' or 'uniform'  
           robust = robust_value,
           mask = cleanmask,
           interactive=False)

    exportfits(imagename=savedir+c_imgname+'.image',
                fitsimage=fitsdir+c_imgname+'.img.fits',
                overwrite=True)

    c_imgname_pbcor = c_imgname+'.pbcor'

    impbcor(imagename=savedir+c_imgname+'.image',
            pbimage=savedir+c_imgname+'.pb',
            outfile=savedir+c_imgname_pbcor+'.image',
            overwrite=True)

    exportfits(imagename=savedir+c_imgname_pbcor+'.image',
                fitsimage=fitsdir+c_imgname_pbcor+'.img.fits',
                overwrite=True)

    # Regrid the cube to MaNGA grid (we used H-alpha map from Pipe3D as the template. The fits header of Pipe3D map was not completed, Hsi-An had to fix the header first before using it as a template.   
    if import_pipe3d == True:
        importfits(fitsimage=pipe3ddir+'manga-'+plateifu+'.Pipe3D.cube.edit.fits', imagename=savedir+'manga-'+plateifu+'.Pipe3D.cube.edit.image')
    
    imregrid(imagename=savedir+c_imgname_pbcor+'.image',
             output=savedir+c_imgname_pbcor+'.regrid.image',
             template=savedir+'manga-'+plateifu+'.Pipe3D.cube.edit.image',axes=[0,1],
             overwrite=True)
    

    exportfits(imagename=savedir+c_imgname_pbcor+'.regrid.image',
               fitsimage=fitsdir+c_imgname_pbcor+'.regrid.img.fits',
               overwrite=True)
     
