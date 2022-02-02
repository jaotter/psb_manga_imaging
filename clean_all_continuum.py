# coding: utf-8

import os

        
plifu_list = ['8655-1902', '9494-3701', '8941-3701', '9194-3702', '8939-3703', '8080-3704', '8086-3704',
              '9088-9102', '7964-1902', '8081-3702', '8083-12703', '8085-6104', '8982-6104']

theoutframe = 'LSRK'
theveltype = 'radio'
restoringbeam = ['2.5arcsec']
chanchunks = -1
niter = 0
robust_value = 0.5
nterms = 1
thecellsize = '0.5arcsec'
theimsize=[256,256]


for plateifu in plifu_list:
    if plateifu != '8655-1902':
        continue
    datadir = '/lustre/cv/observers/cv-12578/data/'
    savedir = datadir+'data_products/target'+plateifu+'/cont_imaging/'
    fitsdir = datadir+'data_products/fitsimages/'
    msdir = datadir+'split_ms/'
    pip3ddir = datadir+'pipe3d/'

    os.chdir(datadir)
    
    fullvis = msdir+'target'+plateifu+'_vis.ms'
    if plateifu == '8081-3702' or plateifu == '9088-9102' or plateifu == '9494-3701':
        fullvis = msdir+'target'+plateifu+'_concat_vis.ms'

    #check if there is continuum or strong line channels
    plotms(vis=fullvis,
           xaxis='channel',
           yaxis='amp',
           spw=0,
           showgui=False,
           plotfile=savedir+'/channel_amp_target'+plateifu+'_spw0.png')
           

    spwrange = '1,2,3,0:'+lower_chan+'~'+upper_chan
    imgname = 'target'+plateifu+'_cont_r'+robust_value+'_exchans:'+lower_chan+'-'+upper_chan
    d_flname = imgname+'.dirty.image'

    #creating dirty cube
    tclean(vis=fullvis,
             imagename=savedir+d_flname,
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
             nterms=nterms,
             chanchunks=chanchunks,
             pbcor=False,
             deconvolver='hogbom',
             weighting = 'briggs', #'briggs' or 'natural' or 'uniform' 
             robust = robust_value,
             interactive=False)

    exportfits(imagename=savedir+d_flname,
               fitsimage=fitsdir+imgname+'.dirty.fits')

    imstats = imstat(savedir+d_imgname)
    imgrms = imstats['rms'][0]
    str_rms = str(round(imgrms, 5))
    c_imgname = imgname'_'+str_rms+'Jy'
    c_flname = c_imgname+'.image'

    tclean(vis=fullvis,
           imagename=savedir+c_flname,
           field=plateifu,
           spw=spwrange,
           restfreq=restfreq,
           threshold=str(cuberms)+'Jy', # rms of cube, we clean down to 1sigma 
           imsize=theimsize,  # we used [256,256], just to make sure there is no weird features outside of the galaxy
           cell=thecellsize,
           outframe=theoutframe,
           restoringbeam=restoringbeam,                                                                               
           specmode='cube',
           gridder='standard',
           veltype=theveltype,
           niter=niter, # we use 2000 or so, a large number anyway.
           nterms=nterms,
           chanchunks=chanchunks,
           pbcor=False,
           deconvolver='hogbom',
           weighting = 'briggs', #'briggs' or 'natural' or 'uniform'  
           robust = robust_value,
           interactive=False)

    exportfits(imagename=savedir+c_flname,
                fitsimage=fitsdir+c_imgname+'.img.fits',
                overwrite=True)

    c_imgname_pbcor = c_imgname+'.pbcor'

    pbcor(imgagename=savedir+c_flname,
          pbimage=savedir+c_imgname+'.pb',
          outfile=savedir+c_imgname_pbcor+'.image')

    exportfits(imagename=savedir+c_imgname_pbcor+'.image',
                fitsimage=fitsdir+c_imgname_pbcor+'.img.fits',
                overwrite=True)

    # Regrid the cube to MaNGA grid (we used H-alpha map from Pipe3D as the template. The fits header of Pipe3D map was not completed, Hsi-An had to fix the header first before using it as a template.   
    importfits(fitsimage=pipe3ddir+'manga-'+plateifu+'.Pipe3D.cube.edit.fits', imagename=savedir+'manga-'+plateifu+'.Pipe3D.cube.edit.image')
    imregrid(imagename=savedir+c_imgname_pbcor+'.image',
             output=savedir+c_imgname_pbcor+'.regrid.image',
             template=savedir+'manga-'+plateifu+'.Pipe3D.cube.edit.image',axes=[0,1])
    

    exportfits(imagename=savedir+c_imgname_pbcor+'.regrid.image', fitsimage=fitsdir++c_imgname_pbcor+'.regrid.img.fits')
     
