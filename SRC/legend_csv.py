#!/usr/bin/env python

from __main__ import lc_class_name, lu_class_name, mr_built_mask_class_name


def labels_from_csv(current_labels):
    '''
    Function that take as input a list of current labels for 'LC' and 'LU' classes and return a list of modified
    labels according to the classes' names provided via "lc_class_name" and "lu_class_name"
    '''
    new_label = []
    lc_class_rename_dict = {}
    lu_class_rename_dict = {}
    mr_class_rename_dict = {}
    if lc_class_name != "":
        for row in open(lc_class_name):
            classcode,classname=row.replace('\r\n','\n').split('\n')[0].split('|')
            lc_class_rename_dict[classcode]=classname
    if lu_class_name != "":
        for row in open(lu_class_name):
            classcode,classname=row.replace('\r\n','\n').split('\n')[0].split('|')
            lu_class_rename_dict[classcode]=classname
    if mr_built_mask_class_name != "":
        for row in open(mr_built_mask_class_name):
            classcode,classname=row.replace('\r\n','\n').split('\n')[0].split('|')
            mr_class_rename_dict[classcode]=classname
    for l in current_labels:
        if l[:2]=='LC':
            classnum=l[3:l.index('_proportion')]
            if classnum in lc_class_rename_dict.keys():
                new_label.append('LC "'+lc_class_rename_dict[classnum]+'"')
            else:
                new_label.append('LC "'+classnum+'"')
        elif l[:2]=='LU':
                        classnum=l[3:l.index('_proportion')]
                        if classnum in lu_class_rename_dict.keys():
                            new_label.append('LU "'+lu_class_rename_dict[classnum]+'"')
                        else:
                            new_label.append('LU "'+classnum+'"')
        elif l[:2]=='MR':
                        classnum=l[3:l.index('_proportion')]
                        if classnum in mr_class_rename_dict.keys():
                            new_label.append('MR "'+mr_class_rename_dict[classnum]+'"')
                        else:
                            new_label.append('MR "'+classnum+'"')
        else:
            new_label.append(l)
    return new_label