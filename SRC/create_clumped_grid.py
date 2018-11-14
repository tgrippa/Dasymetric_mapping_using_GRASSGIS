#!/usr/bin/env python

import sys
import grass.script as gscript


def random_layer_name(prefix='tmp'):
    ### Function that return a name for a temporary layer in GRASS GIS ###
    tmp = gscript.tempfile()
    return prefix + '_' +gscript.basename(tmp).replace('.','_')


def create_clumped_grid(tile_size, mask_raster, output='clumped_grid'):
    '''
    Function creating clumped grid (pixels with unique value) which match with the extend of an existing raster
    'tile_size' is the spatial resolution of the new grid, in meters
    '''
    gscript.run_command('g.region', raster=mask_raster, res=tile_size)
    if gscript.find_file('MASK', element = 'cell')['name']:
        sys.exit("The script stops because there is an active MASK in the mapset. Please remove it first with 'r.mask -r'")
    gscript.run_command('r.mask', quiet=True, raster=mask_raster.split("@")[0])
    tmp=random_layer_name()
    gscript.mapcalc("%s=rand(0 ,999999999)"%tmp, overwrite=True, seed='auto') #Creating a raster with random values
    gscript.run_command('r.clump', quiet=True, input=tmp,output=output,overwrite=True) #Assigning a unique value to each grid
    gscript.run_command('r.mask', quiet=True, flags='r')
    gscript.run_command('g.remove', flags='f', type='raster', name=tmp)
