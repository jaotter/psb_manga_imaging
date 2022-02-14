# coding: utf-8

import os
import csv 

#spw = os.getenv('SPW')

#reduction_type = 'CO_mangabeam'
#reduction_type = 'CO_native_beam'
#reduction_type = 'CO_native_beam_r=-2'
#reduction_type = 'CO_native_beam_r=2'

#reduction_type = 'spw1_r=2'
#reduction_type = 'spw2_r=2'
reduction_type = 'spw3_r=2'

print(reduction_type)

if reduction_type == 'CO_mangabeam':
    robust_value = 0.5
    restoringbeam = ['2.5arcsec']
    spw = '0'
    restfreq = "115.2601925GHz"
    dir_name = 'mangabeam/'
    imgname_end = '_mangabeam_mask'

if reduction_type == 'CO_native_beam':
    robust_value = 0.5
    restoringbeam = 'common'
    spw = '0'
    restfreq = "115.2601925GHz"
    dir_name = 'native_beam/'
    imgname_end = '_mask'

if reduction_type == 'CO_native_beam_r=-2':
    robust_value = -2
    restoringbeam = 'common'
    spw = '0'
    restfreq = "115.2601925GHz"
    dir_name = 'robust_-2/'
    imgname_end = '_mask'

if reduction_type == 'CO_native_beam_r=2':
    robust_value = 2
    restoringbeam = 'common'
    spw = '0'
    restfreq = "115.2601925GHz"
    dir_name = 'robust_+2/'
    imgname_end = '_mask'

if reduction_type == 'spw1_r=2':
    robust_value = 2
    restoringbeam = 'common'
    spw = '1'
    restfreq = "113.5GHz"
    dir_name = 'robust_+2/'
    imgname_end = '_mask'

if reduction_type == 'spw2_r=2':
    robust_value = 2
    restoringbeam = 'common'
    spw = '2'
    restfreq = "107.013831GHz"
    dir_name = 'robust_+2/'
    imgname_end = '_mask'

if reduction_type == 'spw3_r=2':
    robust_value = 2
    restoringbeam = 'common'
    spw = '3'
    restfreq = "100.076392GHz" #v=0, J=11-10
    dir_name = 'robust_+2/'
    imgname_end = '_mask'

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

theoutframe = 'LSRK'
theveltype = 'radio'
chanchunks = -1
niter = 100000
nterms = 1
thecellsize = '0.5arcsec'
theimsize=[256,256]
velwidth='11km/s'

changespw = False

contsub_list = ['8080-3704', '8083-12703', '8086-3704', '8982-6104', '9088-9102', '9194-3702', '9494-3702']
contsub = True

print(plifu_list)

for ind,plateifu in enumerate(plifu_list):

    print('BEGINNING IMAGING FOR '+plateifu+' SPW '+spw)
    datadir = '/lustre/cv/observers/cv-12578/data/'
    savedir = datadir+'data_products/target'+plateifu+'/spw'+spw+'_cube/'
    fitsdir = datadir+'data_products/fitsimages/spw'+spw+'/'+dir_name
    msdir = datadir+'split_ms/'
    pipe3ddir = datadir+'pipe3d/'

    if not os.path.isdir(savedir):
        os.mkdir(savedir)

    os.chdir(datadir)
    
    if plateifu == '8655-3701':
        if spw == '0':
            spw = '1'
            changespw = True
        else: #skip this galaxy if not imaging CO
            continue

    fullvis = msdir+'target'+plateifu+'_vis.ms'
    if plateifu == '8081-3702' or plateifu == '9088-9102' or plateifu == '9494-3701':
        fullvis = msdir+'target'+plateifu+'_concat_vis.ms'

    xpos=str(theimsize[0]/2)
    ypos=str(theimsize[1]/2)
    radius = str(radius_list[ind])
    cleanmask = 'circle[['+xpos+'pix,'+ypos+'pix], '+radius+'pix]'
    print(cleanmask)

    imgname = 'target'+plateifu+'_cube_spw'+spw+'_r'+str(robust_value)+imgname_end
    
    #continuum subtraction only for those that need it
    if plateifu in contsub_list:
        cont_spw = '1,2,3,0:0~'+chan_lower[ind]+';'+chan_upper[ind]+'~1919'
        if contsub == True:
            uvcontsub(vis=fullvis,
                      spw='0,1,2,3',
                      fitspw=cont_spw,
                      excludechans=False,
                      combine='spw',
                      solint='int',
                      fitorder=0,
                      want_cont=False) 

        imgname = imgname + '_contsub'


    d_imgname = imgname+'.dirty'

    #creating dirty cube
    tclean(vis=fullvis,
           imagename=savedir+d_imgname,
           field=plateifu,
           spw=spw,
           restfreq=restfreq,
           threshold='1Jy', # high threshold for dirty cube  
           imsize=theimsize,  # we used [256,256], just to make sure there is no weird features outside of the galaxy
           cell=thecellsize,
           outframe=theoutframe,
           restoringbeam=restoringbeam,  # to match MaNGA resolution,  # “common” will give you the native beam size of this observation, use restoringbeam=[’2.5arcsec’] to generate a map with resolution similar to that of MaNGA. 
           specmode='cube',
           gridder='standard',
           width=velwidth,
           veltype=theveltype,
           niter=0, # 0 for dirty cube
           pbcor=False,
           deconvolver='hogbom',
           weighting = 'briggs', #'briggs' or 'natural' or 'uniform' 
           robust = robust_value,
           mask = cleanmask,
           interactive=False)

    #exportfits(imagename=savedir+d_imgname+'.image',
    #           fitsimage=fitsdir+d_imgname+'.fits',
    #           overwrite=True)

    imstats = imstat(savedir+d_imgname+'.image')
    imgrms = imstats['rms'][0]
    str_rms = str(round(imgrms, 5))
    c_imgname = imgname+'_'+str_rms+'Jy'

    tclean(vis=fullvis,
           imagename=savedir+c_imgname,
           field=plateifu,
           spw=spw,
           restfreq=restfreq,
           threshold=str(imgrms)+'Jy', # rms of cube, we clean down to 1sigma
           imsize=theimsize,  # we used [256,256], just to make sure there is no weird features outside of the galaxy                               
           cell=thecellsize,
           outframe=theoutframe,
           restoringbeam=restoringbeam,
           specmode='cube',
           gridder='standard',
           width=velwidth,
           veltype=theveltype,
           niter=niter,
           pbcor=False,
           deconvolver='hogbom',
           weighting = 'briggs', #'briggs' or 'natural' or 'uniform'       
           robust = robust_value,
           mask = cleanmask,
           interactive=False)

    exportfits(imagename=savedir+c_imgname+'.image',
                fitsimage=fitsdir+c_imgname+'.cube.fits',
                overwrite=True)

    c_imgname_pbcor = c_imgname+'.pbcor'

    impbcor(imagename=savedir+c_imgname+'.image',
            pbimage=savedir+c_imgname+'.pb',
            outfile=savedir+c_imgname_pbcor+'.image',
            overwrite=True)

    exportfits(imagename=savedir+c_imgname_pbcor+'.image',
                fitsimage=fitsdir+c_imgname_pbcor+'.cube.fits',
                overwrite=True)

    # Regrid the cube to MaNGA grid (we used H-alpha map from Pipe3D as the template. The fits header of Pipe3D map was not completed, Hsi-An had to fix the header first before using it as a template.
    if not os.path.exists(savedir+'manga-'+plateifu+'.Pipe3D.cube.edit.image'):
        importfits(fitsimage=pipe3ddir+'manga-'+plateifu+'.Pipe3D.cube.edit.fits', imagename=savedir+'manga-'+plateifu+'.Pipe3D.cube.edit.image')

    imregrid(imagename=savedir+c_imgname_pbcor+'.image',
             output=savedir+c_imgname_pbcor+'.regrid.image',
             template=savedir+'manga-'+plateifu+'.Pipe3D.cube.edit.image',axes=[0,1],
             overwrite=True)


    exportfits(imagename=savedir+c_imgname_pbcor+'.regrid.image',
               fitsimage=fitsdir+c_imgname_pbcor+'.regrid.cube.fits',
               overwrite=True)

    if changespw == True:
        spw = '0'
        changespw = False
