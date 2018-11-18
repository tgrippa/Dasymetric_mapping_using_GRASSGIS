#!/usr/bin/env python


import os
import grass.script as gscript


def data_prep(categorical_raster):
    '''
    Function that extracts resolution and sorted list of classes of 
    a categorical raster (like land cover or land use information).
    '''
    info = gscript.raster_info(categorical_raster)
    nsres=info.nsres
    ewres=info.ewres
    L = []
    L=[cl.split("	")[0] for cl in gscript.parse_command('r.category',map=categorical_raster)]
    for i,x in enumerate(L):  #Make sure the format is UTF8 and not Unicode
        L[i]=x.encode('UTF8')
    L.sort(key=float) #Sort the raster categories in ascending.
    return nsres, ewres, L