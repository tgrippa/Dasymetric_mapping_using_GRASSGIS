#!/usr/bin/env python

import grass.script as gscript

def random_layer_name(prefix='tmp'):
    ### Function that return a name for a temporary layer in GRASS GIS ###
    tmp = gscript.tempfile()
    return prefix + '_' +gscript.basename(tmp).replace('.','_')
