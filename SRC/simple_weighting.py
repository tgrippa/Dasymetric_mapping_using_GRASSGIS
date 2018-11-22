#!/usr/bin/env python


from __main__ import *


import os
import csv
import grass.script as gscript


def create_simple_weighting_layer_from_df(df_grid, weight_column, clumped_grid, testlabel):
    '''
    Function that creates a weighting layer simply by using weights available in a column of a dataframe containing grid level variables
    '''
    ## Define a reclassification rule
    cat_list=df_grid['cat'].tolist()
    weight_list=df_grid[weight_column].tolist()
    rule=""
    for i, cat in enumerate(cat_list):
        rule+=str(cat)
        rule+="="
        rule+=str(int(round((weight_list[i]*10000),0)))  #reclass rule of r.reclass requier INTEGER values but random forest prediction could be very low values.
        rule+="\n"
    rule+="*"
    rule+="="
    rule+="NULL"
    ## Create a temporary 'weight_reclass_rules.csv' file for r.reclass
    outputcsv="%s_weight_reclass_rules.csv"%gscript.tempfile()
    TMP_CSV.append(outputcsv)
    f = open(outputcsv, 'w')
    f.write(rule)
    f.close()

    # Name of the weighting layer to produce
    output_weighting_layer = "Test_%s_weight"%testlabel
    ## Reclass segments raster layer
    gscript.run_command('g.region', raster=clumped_grid)
    gscript.run_command('r.reclass', quiet=True, overwrite=True,
                        input=clumped_grid, output="weight_int", rules=outputcsv)
    gscript.run_command('r.mapcalc', expression="%s=float(weight_int)/float(10000)"%output_weighting_layer,
                        quiet=True, overwrite=True)

    test_folder = os.path.join(outputdirectory_results,"Test_%s"%testlabel)

    #Create folder where to save the plot if not exists
    if not os.path.exists(test_folder):
        os.makedirs(test_folder)

    function_log = "-------------- TEST %s --------------\n"%testlabel
    function_log += "Simple weighting layer (not RF) based on '%s' \n\n"%weight_column
    fout = open(os.path.join(test_folder,'Test_%s_log_weight_creation.txt'%test), 'w')
    fout.write(function_log)
    fout.close()

    return function_log