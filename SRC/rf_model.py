#!/usr/bin/env python


from __main__ import *


import os
import csv
import math as ma
import time
import shutil
import matplotlib.pyplot as plt
import grass.script as gscript


try:
    from sklearn.ensemble import RandomForestRegressor
    from sklearn.feature_selection import SelectFromModel
    from sklearn.model_selection import GridSearchCV
except:
    gscript.fatal("Scikit learn 0.18 or newer is not installed")


def random_layer_name(prefix='tmp'):
    ### Function that return a name for a temporary layer in GRASS GIS ###
    tmp = gscript.tempfile()
    return prefix + '_' +gscript.basename(tmp).replace('.','_')


def RandomForest(vector,id, lc_classes, lu_classes, mr_classes, layer_to_mask_weights, built_up_pixels, testlabel):
    '''
    Function that creates a random forest model trained at the administrative units level to generate gridded prediction
    covariates are proportion of each Land Cover's class (opt: with proportion of each land use's class)
    '''
    global gridded_vector, n_jobs, kfold

    #Create a string variable to be use to save function log
    function_log = "-------------- TEST %s --------------\n"%testlabel
    function_log += "Random Forest classifier for creating the weighting layer\n"
    function_log += "VHR land cover classes used: %s \n"%(", ".join(lc_classes) if len(lc_classes)>0 else 'None')
    function_log += "VHR land use classes used: %s \n"%(", ".join(lu_classes) if len(lu_classes)>0 else 'None')
    function_log += "MR built-up classe used: %s \n"%(", ".join(mr_classes) if len(mr_classes)>0 else 'None')
    function_log += "Layer '%s' used to force zero weights when proportion of class '%s' is null\n"%(layer_to_mask_weights, "', '".join(built_up_pixels))

    #Create folder where to save the plot if not exists
    test_folder = os.path.join(outputdirectory_results,"Test_%s"%testlabel)
    if not os.path.exists(test_folder):
        os.makedirs(test_folder)

    # Define the path to the file with all co-variates
    all_stats_grid=os.path.join(outputdirectory_grid,"all_stats.csv") # for grid level
    all_stats_admin=os.path.join(outputdirectory_admin,"all_stats.csv") # for admin level
    # -------------------------------------------------------------------------
    # Data preparation for administrative units (compute natural log of response variable)
    # -------------------------------------------------------------------------
    # Export desired columns from the attribute table as CSV
    tmp_table=os.path.join(outputdirectory_admin,"%s.csv"%random_layer_name()) # Define the path to the .csv
    query="SELECT cat,%s FROM %s"%(response_column,gridded_vector.split('@')[0])
    gscript.run_command('db.select', quiet=True, sql=query, output=tmp_table)
    TMP_CSV.append(tmp_table)
    # Compute log of the response variable in a new .csv file
    reader=csv.reader(open(tmp_table,'r'), delimiter='|')
    log_response_csv=os.path.join(outputdirectory_admin,"log_response_variable.csv") # Define the path to the .csv containing the log of the response variable
    fout=open(log_response_csv,'w')
    writer=csv.writer(fout, delimiter=',')
    new_content=[]
    new_header=['cat','log_response']
    new_content.append(new_header)
    reader.next() # Pass the header
    [new_content.append([row[0],ma.log(float(row[1]))]) for row in reader]  # Compute natural log (ln) of the response variable
    writer.writerows(new_content)
    time.sleep(0.5) # To be sure the file will not be close to fast (the content could be uncompletly filled)
    fout.close()
    # For admin level : join all co-variates with the log of respons variable
    tmp_file=join_2csv(log_response_csv,all_stats_admin,separator=",",join='inner',fillempty='NULL')
    admin_attribute_table=os.path.join(outputdirectory_admin,"admin_attribute_table.csv")
    shutil.copy2(tmp_file,admin_attribute_table) # Copy the file from temp folder to admin folder
    TMP_CSV.append(tmp_file)

    # -------------------------------------------------------------------------
    # Creating RF model
    # -------------------------------------------------------------------------
    print "Working of random forest model..."
    df_admin = pd.read_csv(admin_attribute_table) #reading the csv file as dataframe
    df_grid = pd.read_csv(all_stats_grid)

    ## Make a list with name of covariables columns
    list_covar=[]
    for cl in lc_classes:
        list_covar.append("LC_%s_proportion"%cl)
    for cl in lu_classes:
        list_covar.append("LU_%s_proportion"%cl)
    for cl in mr_classes:
        list_covar.append("MR_%s_proportion"%cl)

    ## Saving variable to predict (response variable)
    y = df_admin['log_response']

    ## Saving covariable for prediction (independent variables)
    x=df_admin[list_covar]  #Get a dataframe with independent variables for administratives units
    #x.to_csv(path_or_buf=os.path.join(outputdirectory_admin,"covar_x.csv"), index=False) #Export in .csv for archive
    # Remove features whose importance is less than a threshold (Feature selection)
    rfmodel=RandomForestRegressor(n_estimators = 500, oob_score = True, max_features='auto', n_jobs=-1, random_state=0)  #random_state is fixed to allow exact replication
    a=SelectFromModel(rfmodel, threshold=min_fimportance)
    fited=a.fit(x, y)
    feature_idx = fited.get_support()   # Get list of True/False values according to the fact the OOB score of the covariate is upper the threshold
    list_covar = list(x.columns[feature_idx])  # Update list of covariates with the selected features
    x=fited.transform(x)  # Replace the dataframe with the selected features
    message="Selected covariates for the random forest model (with feature importance upper than {value} %) : \n".format(value=min_fimportance*100)  # Print the selected covariates for the model
    message+="\n".join(list_covar)
    function_log+=message+'\n\n'

    #### Tuning of hyperparameters for the Random Forest regressor using "Grid search"
    print "... starting grid search for RF hyperparameters..."
    # Instantiate the grid search model
    grid_search = GridSearchCV(estimator=RandomForestRegressor(random_state=0), param_grid=param_grid, cv=kfold, n_jobs=n_jobs, verbose=0)
    grid_search.fit(x, y)   # Fit the grid search to the data
    regressor = grid_search.best_estimator_  # Save the best regressor
    regressor.fit(x, y) # Fit the best regressor with the data
    # Print infos and save it in the logfile - Grid of parameter to be tested
    message='Parameter grid for Random Forest tuning :\n'
    for key in param_grid.keys():
        message+='    '+key+' : '+', '.join([str(i) for i in list(param_grid[key])])+'\n'
    function_log+=message+'\n'
    # Print infos and save it in the logfile - Tuned parameters
    message='Optimized parameters for Random Forest after grid search %s-fold cross-validation tuning :\n'%kfold
    for key in grid_search.best_params_.keys():
        message+='    %s : %s'%(key,grid_search.best_params_[key])+'\n'
    function_log+=message+'\n'
    # Print info of the mean cross-validated score (OOB) and stddev of the best_estimator
    best_score=grid_search.cv_results_['mean_test_score'][grid_search.best_index_]
    best_std=grid_search.cv_results_['std_test_score'][grid_search.best_index_]
    message="Mean cross-validated score (OOB) and stddev of the best_estimator : %0.3f (+/-%0.3f)"%(best_score,best_std)+'\n'
    function_log+=message+'\n'
    # Print mean OOB and stddev for each set of parameters
    means = grid_search.cv_results_['mean_test_score']
    stds = grid_search.cv_results_['std_test_score']
    message="Mean cross-validated score (OOB) and stddev for every tested set of parameter :\n"
    for mean, std, params in zip(means, stds, grid_search.cv_results_['params']):
        message+="%0.3f (+/-%0.03f) for %r"% (mean, std, params)+'\n'
    function_log+=message+'\n'
    # Print final model OOB
    message='Final Random Forest model run - internal Out-of-bag score (OOB) : %0.3f'%regressor.oob_score_
    function_log+=message+'\n'
    #### Prediction
    print "... starting prediction of weights..."
    # Predict on grids
    x_grid=df_grid[list_covar] #Get a dataframe with independent variables for grids (remaining after feature selection)
    #x_grid.to_csv(path_or_buf=os.path.join(outputdirectory_grid,"covar_x_grid.csv"), index=False) #Export in .csv for archive
    prediction = regressor.predict(x_grid)  # Apply the model on grid values
    # Save the prediction
    df1 = df_grid['cat']
    df2 = pd.DataFrame(prediction, columns=['log'])
    df_weight = pd.concat((df1,df2), axis=1)
    col = df_weight.apply(lambda row : np.exp(row["log"]), axis=1)  #Use exponential to 'un-log' the prediction
    df_weight ["weight_after_log"] = col
    weightcsv=os.path.join(outputdirectory_grid,"weight.csv")
    df_weight.to_csv(path_or_buf=weightcsv) #Export in .csv for archive
    ## Define a reclassification rule
    print "\nCreation of weighting layer..."
    cat_list=df_weight['cat'].tolist()
    weight_list=df_weight['weight_after_log'].tolist()
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
    outputcsv=os.path.join(outputdirectory_grid,"weight_reclass_rules.csv")
    TMP_CSV.append(outputcsv)
    f = open(outputcsv, 'w')
    f.write(rule)
    f.close()
    ## Reclass segments raster layer
    gscript.run_command('g.region', raster=clumped_grid)
    gscript.run_command('r.reclass', quiet=True, overwrite=True, input=clumped_grid, output="weight_int", rules=outputcsv)
    gscript.run_command('r.mapcalc', expression="weight_float=float(weight_int)/float(10000)", quiet=True, overwrite=True) #Get back to the original 'float' prediction of population density of random forest
    TMP_MAPS.append("weight_int")
    TMP_MAPS.append("weight_float")

    ## Save the final output and force weight to zero if no built-up pixel in the grid if desired
    weigthing_layer_name = "Test_%s_weight"%testlabel  # Name of the weighting layer to produce
    gscript.run_command('r.mask', overwrite=True, raster='maskcopy')  # Apply mask
    if len(built_up_pixels) == 0:
        gscript.run_command('r.mapcalc',expression="%s=weight_float"%weigthing_layer_name, quiet=True, overwrite=True)
    else:
        # Set the region
        gscript.run_command('g.region', raster='clumped_grid')
        # Define the name of the prefix corresponding to the binary layer according to the name of the raster definedin 'layer_to_mask_weights'
        if layer_to_mask_weights == Land_cover:
            inputlayer_prefix = 'LC'
        elif layer_to_mask_weights == Land_use:
            inputlayer_prefix = 'LU'
        elif layer_to_mask_weights == mr_builtup:
            inputlayer_prefix = 'MR'
        ## Create r.mapcalc formula to be used for masking built pixels in the weight layer
        formula = "%s="%weigthing_layer_name
        # Iterate according to the lenght of the 'built_up_pixels' list
        TO_REMOVE = []
        for built_up_pixel in built_up_pixels:
            input_layer = '%s_%s'%(inputlayer_prefix,built_up_pixel)
            resamp_layer = 'sum_%s'%input_layer
            gscript.run_command('r.resamp.stats', quiet=True, overwrite=True, input=input_layer, output=resamp_layer, method='sum')
            TO_REMOVE.append(resamp_layer)
            formula += "if(%s!=0,weight_float,"%resamp_layer
        formula += "0"
        for built_up_pixel in built_up_pixels:
            formula += ")"
        # Apply to formula through r.mapcalc
        gscript.run_command('r.mapcalc',expression=formula, quiet=True, overwrite=True)
        # Remove temporary layers for masking built pixels
        [gscript.run_command('g.remove', flags='f', type='raster', name=rast) for rast in TO_REMOVE]
    gscript.run_command('r.mask', flags='r')  # Remove mask

    # -------------------------------------------------------------------------
    # Feature importances
    # -------------------------------------------------------------------------
    print "\nCreation of feature importance plot...\n\n"
    importances = regressor.feature_importances_  #Save feature importances from the model
    indices = np.argsort(importances)[::-1]
    x_axis = importances[indices][::-1]
    idx = indices[::-1]
    y_axis = range(x.shape[1])
    plt.figure(figsize=(4, (len(y_axis)+1)*0.23))  #Set the size of the plot according to the number of features
    plt.scatter(x_axis,y_axis)
    Labels = []
    for i in range(x.shape[1]):
        Labels.append(x_grid.columns[idx[i]])
    Labels=labels_from_csv(Labels)  #Change the labels of the feature according to 'lc_classes_list' and 'lu_classes_list'
    plt.yticks(y_axis, Labels)
    plt.ylim([-1,len(y_axis)])  #Ajust ylim
    plt.xlim([-0.02,max(x_axis)+0.02]) #Ajust xlim
    plt.title("Feature importances")
    path_plot = os.path.join(test_folder,"Test_%s_RF_feature_importance"%testlabel)
    plt.savefig(path_plot+'.png', bbox_inches='tight', dpi=400)  # Export in .png file (image)
    plt.savefig(path_plot+'.eps', bbox_inches='tight', dpi=400)  # Export in .svg file (vectorial)
    plt.close()  # Prevent the plot to be displayed at this stage of the script

    # Save the log
    fout = open(os.path.join(test_folder,'Test_%s_log_weight_creation.txt'%testlabel), 'w')
    fout.write(function_log)
    fout.close()

    # Print the log before creating the plot
    print function_log
    # Return the log and plot
    return function_log, path_plot+'.png'
