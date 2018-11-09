#!/usr/bin/env python

import grass.script as gscript
import multiprocessing
from multiprocessing import Pool
from functools import partial


def clip(name):
    """ Define a short function for the clip operation """
    global suffix, o
    try:
        gscript.run_command('r.clip', overwrite=o, input=name, output='%s_%s'%(name,suffix))
        return "'%s' has been cliped"%name
    except:
        return "ERROR: '%s' has not been cliped."%name


def clip_multiple_raster(raster_name_list, output_suffix='clip', overwrite=False, n_jobs=2):
    """ Define the function to clip a collection of rasters.
    Please be carefull that the clip will be based on region extend and pixels under MASK will be null.
    Please take care of well defining the computational region and a MASK if desired before calling the function.
    """
    global suffix, o
    o = overwrite
    suffix = output_suffix
    # Clip the rasters in multiprocessing pool of jobs
    p = Pool(n_jobs)
    output = p.map(clip, raster_name_list)  # Launch the processes for as many items in the list (if function with a return, the returned results are ordered thanks to 'map' function)
    p.close()
    p.join()
    print "\n".join(output)
