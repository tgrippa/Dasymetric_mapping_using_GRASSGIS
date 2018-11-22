#!/usr/bin/env python


from __main__ import outputdirectory_results, clumped_grid, TMP_MAPS, TMP_CSV


import os
import grass.script as gscript
import math as ma
import pandas as pd
import numpy as np


def random_layer_name(prefix='tmp'):
    ### Function that return a name for a temporary layer in GRASS GIS ###
    tmp = gscript.tempfile()
    return prefix + '_' +gscript.basename(tmp).replace('.','_')


def get_ref_and_prediction_table(vector_admin_layer, ref_column, pop_column, prediction_raster_pop):
    # Define region to match the resolution and extend of the grid layer
    gscript.run_command('g.region', raster=clumped_grid)
    # Create raster with administrative unit ids
    reference_raster_id = random_layer_name()
    reference_raster_pop = random_layer_name()
    TMP_MAPS.append(reference_raster_id)
    TMP_MAPS.append(reference_raster_pop)
    gscript.run_command('v.to.rast', overwrite=True, quiet=True, input=vector_admin_layer,
                        output=reference_raster_id, use='attr', attribute_column=ref_column)
    gscript.run_command('v.to.rast', overwrite=True, quiet=True, input=vector_admin_layer,
                        output=reference_raster_pop, use='attr', attribute_column=pop_column)

    #Get id for each administrative zones in a list
    tmp_file = gscript.tempfile()
    TMP_CSV.append(tmp_file)
    gscript.run_command('r.univar', flags='et', overwrite=True, map=reference_raster_id,
                        zones=reference_raster_id, output=tmp_file, separator='comma')
    fin = open(tmp_file)
    fin.next()
    id_list = [int(row.split(",")[4]) for row in fin] #4 refers to r.univar output for 'min' stat

    #Get the reference population count for each administrative zones in a list
    tmp_file=gscript.tempfile()
    TMP_CSV.append(tmp_file)
    gscript.run_command('r.univar', flags='et', overwrite=True, map=reference_raster_pop,
                        zones=reference_raster_id, output=tmp_file, separator='comma')
    fin = open(tmp_file)
    fin.next()
    ref_list = [float(row.split(",")[4]) for row in fin] #4 refers to r.univar output for 'min' stat

    #Get the sum of prediction of population for each administrative zones in a list
    tmp_file=gscript.tempfile()
    gscript.run_command('r.univar', flags='et', overwrite=True, map=prediction_raster_pop,
                        zones=reference_raster_id, output=tmp_file, separator='comma')
    fin = open(tmp_file)
    fin.next()
    predict_list = [float(row.split(",")[12]) for row in fin] #12 refers to r.univar output for 'sum' stat

    return pd.DataFrame({'Id':id_list,'Reference':ref_list,'Prediction':predict_list})


def compute_validation_statistics(df, output_csv=""):
    #### Compute validation statistics for each administrative unit ####
    #Compute error
    df['error'] = df['Prediction']-df['Reference']
    #Compute percentage error raster
    df['prcterror'] = df['error']/df['Reference']*100
    #Compute squared error raster
    df['sqerror'] = df['error']**2
    #Compute absolute error raster
    df['abserror'] = abs(df['error'])

    if output_csv:
        df.to_csv(output_csv, index=False)


def validation(vector_admin_layer, ref_column, pop_column, testlabel):
    # Get paths to the outputfiles of the function
    test_folder = os.path.join(outputdirectory_results,"Test_%s"%testlabel)
    output_csv_validation = os.path.join(test_folder,"Test_%s_attribute_table_validation.csv"%testlabel)
    output_log_validation = os.path.join(test_folder,"Test_%s_log_validation.txt"%testlabel)
    # Get the name of the prediction layer
    prediction_raster_pop = 'Test_%s_prediction'%testlabel
    ## Get a dataframe with unit 'id', reference value and predicted value
    df = get_ref_and_prediction_table(vector_admin_layer, ref_column, pop_column, prediction_raster_pop)
    ## Compute validation statistics for each administrative unit
    compute_validation_statistics(df,output_csv_validation)

    #### Compute overall validation statistics ####
    rmse = ma.sqrt(round(df['sqerror'].mean(),2))  #Compute RMSE (Root mean squared error)
    mean_ref = df['Reference'].mean()  #Compute mean reference population per admin unit
    prct_rmse = (rmse/mean_ref)*100  #Compute %RMSE (Root mean squared error in percentage of the mean reference population by grid)
    MAE = df['abserror'].mean()  #Compute MAE (Mean absolute error)
    TAE = df['abserror'].sum()  #Compute TAE (Total absolute error)
    POPTOT = df['Reference'].sum() #Compute Total reference population
    PREDTOT = df['Prediction'].sum() #Compute Total reference population
    RTAE = TAE/POPTOT  #Compute RTAE (Relative total absolute error)
    corr = np.corrcoef(df['Reference'],df['Prediction'])[0,1]  #Get correlation value
    r_squared = (corr**2)  #Get r-squared value

    #### Outputs print and log
    function_log = "-------------- TEST %s --------------\n"%testlabel
    function_log+="Reference vector : %s \n"%vector_admin_layer.split("@")[0]
    function_log+="Prediction raster : %s \n"%prediction_raster_pop.split("@")[0]
    function_log+="\n"
    function_log+="Total reference population = %s \n"%round(POPTOT,1)
    function_log+="Total predicted population = %s \n"%round(PREDTOT,1)
    function_log+="Number of reference admin zones = %s \n"%df['Reference'].count()
    function_log+="Number of validation admin zones = %s \n"%df['Prediction'].count()
    function_log+='\n'
    function_log+="Mean reference population count per administrative unit = %s \n"%round(mean_ref,3)
    function_log+="Mean absolute error of prediction (MAE) = %s \n"%round(MAE,3)
    function_log+="Root mean squared error of prediction (RMSE) = %s \n"%round(rmse,3)
    function_log+="Root mean squared error of prediction in percentage (Percent_RMSE) = %s \n"%round(prct_rmse,3)
    function_log+="Total absolute error (TAE) = %s \n"%round(TAE,3)
    function_log+="Relative total absolute error (RTAE) = %s \n"%round(RTAE,3)
    function_log+="R squared = %s \n"%round(r_squared,3)
    if output_log_validation:
        fout = open(output_log_validation, 'w')
        fout.write(function_log)
        fout.close()

    ## Return
    return df, function_log