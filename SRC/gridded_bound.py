#!/usr/bin/env python


import os
import grass.script as gscript

def gridded_admin_boundaries(input_vector, id, list_of_columns, grid):
    '''
    Function convecting the vector to raster then raster to vector: boundaries will have a "staircase" appearence
    so that each tile of the gridded vector will be contained in only one administrative unit
    '''
    def random_layer_name(prefix='tmp'):
        ### Function that return a name for a temporary layer in GRASS GIS ###
        tmp = gscript.tempfile()
        return prefix + '_' +gscript.basename(tmp).replace('.','_')

    def check_no_missing_zones(vector_origin, vector_gridded, resolution):
        '''
        Function checking if the number of items (admin zones) in the original vector provided by the user is wall conserved after the rasterization.
        If the original vector contains small sized polygons (or very tight) and desired 'tile_size' is too large, some polygons could disappeared during the rasterization process
        '''
        origin_n=gscript.parse_command('v.db.univar', flags='g', map=vector_origin, column='cat')['n']
        gridded_n=gscript.parse_command('v.db.univar', flags='g', map=vector_gridded, column='cat')['n']
        if origin_n != gridded_n:
            gscript.run_command('g.remove', quiet=True, type='vector', name=vector_gridded, flags='fb')
            message=_(("A tile size of %s m seems too large and produce loss of some polygons when rasterizing them.\n") % resolution)
            message+=_(("Try to reduce the 'tile_size' parameter or edit the <%s> vector to merge smallest administrative units with their neighoring units") % vector_origin)
            gscript.fatal(message)

    current_mapset = gscript.gisenv()['MAPSET']
    gscript.run_command('g.region', raster=grid)
    resolution = int(float(gscript.parse_command('g.region', flags='pg')['nsres']))
    global gridded_admin_units
    global gridded_vector
    gridded_admin_units = random_layer_name(prefix='gridded_admin_units')
    gridded_vector = input_vector.split("@")[0]+'_'+str(resolution)+'m_gridded'
    gscript.run_command('v.to.rast', quiet=True, input=input_vector, type='area',
                        output=gridded_admin_units, use='attr',
                        attribute_column=id, overwrite=True)
    gscript.run_command('r.to.vect', quiet=True, input=gridded_admin_units,
                        output='%s@%s'%(gridded_vector,current_mapset), type='area', column=id,
                        flags='v',overwrite=True)
    tmp_name=random_layer_name()
    gscript.run_command('g.copy', quiet=True, vector='%s,%s'%(input_vector,tmp_name))
    gscript.run_command('v.db.join', quiet=True, map_=gridded_vector, column='cat',
                        other_table=tmp_name, other_column=id, subset_columns=','.join(list_of_columns)) #join the population count
    gscript.run_command('g.remove', quiet=True, flags='f', type='vector', name=tmp_name+'@'+current_mapset)
    check_no_missing_zones(input_vector, gridded_vector, resolution)
    return gridded_admin_units, gridded_vector