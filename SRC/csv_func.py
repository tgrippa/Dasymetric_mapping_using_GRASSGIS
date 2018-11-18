#!/usr/bin/env python


import os 
import glob
import grass.script as gscript


def atoi(text):
    '''
    Function that return integer if text is digit - Used in 'natural_keys' function
    '''
    return int(text) if text.isdigit() else text


def natural_keys(text):   #Return key to be used for sorting string containing numerical values - Used in 'join_csv' function
    '''
    Trick was found here
    https://stackoverflow.com/questions/5967500/how-to-correctly-sort-a-string-with-a-number-inside
    alist.sort(key=natural_keys) sorts in human order
    http://nedbatchelder.com/blog/200712/human_sorting.html
    (See Toothy's implementation in the comments)

    '''
    import re  #Import needed library
    return [ atoi(c) for c in re.split('(\d+)', text) ]  #Split the string


def ordered_list_of_path(indir,pattern_A,pattern_B="",pattern_C=""):
    '''
    Function that return a list of ordered path for the files in the folder 'indir'.
    'pattern_A', 'pattern_B', 'pattern_C'
    '''
    # Make a list of .csv files according to their filename pattern
    os.chdir(indir) # Change the current directory to the folder containing all the .csv files
    csvList=glob.glob(pattern_A) #Make a list of strings with the name of .csv files
    csvList.sort(key=natural_keys) #Sort the list on a human natural order (for strings containing numericals)
    if pattern_B !="":
        csvList_B=glob.glob(pattern_B) #Make a list of strings with the name of .csv files
        csvList_B.sort(key=natural_keys) #Sort the list on a human natural order (for strings containing numericals)
        for item in csvList_B:
            csvList.append(item)
    if pattern_C !="":
        csvList_C=glob.glob(pattern_C) #Make a list of strings with the name of .csv files
        csvList_C.sort(key=natural_keys) #Sort the list on a human natural order (for strings containing numericals)
        for item in csvList_C:
            csvList.append(item)
    return csvList

def join_2csv(file1,file2,separator=";",join='inner',fillempty='NULL'):
    '''
    Function that join two csv files according to the first column (primary key).
    'file1' and 'file2' wait for complete path (strings) to the corresponding files. Please not that 'file1' is assume to be the left-one in the join
    'separator' wait for the character to be considered as .csv delimiter (string)
    'join' parameter wait either for 'left' or 'inner' according to type of join
    'fillempty' wait for the string to be use to fill the blank when no occurance is found for the join operation
    '''
    import time,csv,os
    header_list=[]
    file1_values_dict={}
    file2_values_dict={}
    reader1=csv.reader(open(file1), delimiter=separator) #Csv reader for file 1
    reader2=csv.reader(open(file2), delimiter=separator) #Csv reader for file 2
    # Make a list of headers
    header_list1=[ x for x in reader1.next()]
    header_list2=[ x for x in reader2.next()[1:]]
    # Make a list of unique IDs from the first and second table according to type of join
    if join=='inner':
        id_list=[row[0] for row in reader1]
        [id_list.append(row[0]) for row in reader2]
        id_list=list(set(id_list))
        id_list.sort(key=natural_keys)
    if join=='left':
        id_list=[row[0] for row in reader1]
        id_list=list(set(id_list))
        id_list.sort(key=natural_keys)
    # Build dictionnary for values of file 1
    reader1=csv.reader(open(file1), delimiter=separator)
    reader1.next()
    values_dict1={rows[0]:rows[1:] for rows in reader1}
    # Build dictionnary for values of file 2
    reader2=csv.reader(open(file2), delimiter=separator)
    reader2.next()
    values_dict2={rows[0]:rows[1:] for rows in reader2}
    # Built new content
    new_content=[]
    new_header=header_list1+header_list2
    new_content.append(new_header)
    for key in id_list:
        new_row=[key]
        try:
            [new_row.append(value) for value in values_dict1[key]]
        except:
            [new_row.append('%s'%fillempty) for x in header_list1[1:]]
        try:
            [new_row.append(value) for value in values_dict2[key]]
        except:
            [new_row.append('%s'%fillempty) for x in header_list2]
        new_content.append(new_row)
    #Return the result
    outfile=gscript.tempfile()
    fout=open(outfile,"w")
    writer=csv.writer(fout, delimiter=separator)
    writer.writerows(new_content) #Write multiples rows in the file
    time.sleep(0.5) # To be sure the file will not be close to fast (the content could be uncompletly filled)
    fout.close()
    return outfile

def join_multiplecsv(fileList,outfile,separator=";",join='inner', fillempty='NULL', overwrite=False):
    '''
    Function that apply join on multiple csv files
    '''
    import os, sys, shutil
    # Stop execution if outputfile exitst and can not be overwriten
    if os.path.isfile(outfile) and overwrite==False:
        print "File '%s' aleady exists and overwrite option is not enabled."%outfile
    else:
        if os.path.isfile(outfile) and overwrite==True:  # If outputfile exitst and can be overwriten
            os.remove(outfile)
            #print "File '%s' will be overwrited."%outfile   # Uncomment if you want a print
        nbfile=len(fileList)
        if nbfile<=1: #Check if there are at least 2 files in the list
            sys.exit("This function require at least two .csv files to be jointed together.")
        # Copy the list of file in a queue list
        queue_list=list(fileList)
        # Left join on the two first files
        file1=queue_list.pop(0)
        file2=queue_list.pop(0)
        tmp_file=join_2csv(file1,file2,separator=separator,join=join, fillempty=fillempty)
        # Left join on the rest of the files in the list
        while len(queue_list)>0:
            file2=queue_list.pop(0)
            tmp_file=join_2csv(tmp_file,file2,separator=separator,join=join, fillempty=fillempty)
        #Copy the temporary file to the desired output path
        shutil.copy2(tmp_file,outfile)
        # Print what happend
        #print "%s individual .csv files were joint together."%nbfile    # Uncomment if you want a print

