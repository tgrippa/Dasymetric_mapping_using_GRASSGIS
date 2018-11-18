#!/usr/bin/env python


import os
import grass.script as gscript

def create_tempdirs(list_of_directories):
    '''
    Function that create needed temporary folder. Those name have to be saved as other function will depend of the name of those folder.
    '''
    return_list = []
    tmp_grass_dir=gscript.tempdir()
    
    for directory in list_of_directories:    
        # Temporary directory for administrative units statistics
        outputdirectory=os.path.join(tmp_grass_dir,directory)
        if not os.path.exists(outputdirectory):
            os.makedirs(outputdirectory)
        return_list.append(outputdirectory)
    # Return paths
    return return_list