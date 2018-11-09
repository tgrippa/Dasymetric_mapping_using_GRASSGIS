#!/usr/bin/env python

"""
Function that apply a color scheme on a raster. 
Takes a KEY=VALUE dictionnary as input with pixel value as KEY and color (R:G:B) as VALUE
"""

import grass.script as gscript

def create_color_rule(color_dict):
    #### Define color table. Replace with the RGB values of wanted colors of each class
    # Check is all keys in the dictionary are either 'int' or 'float'
    if not all([type(key)==int or type(key)==float for key in color_dict.keys()]):
        sys.exit("The keys of the dictionnary should be 'int' or 'float'")
    
    # Get a sorted list with all keys (pixels values)
    sorted_list = [key for key in color_dict.keys()]
    sorted_list.sort()
    
    # Generate the content of the color file
    content = "\n".join(["%s %s"%(key,color_dict[key]) for key in sorted_list])
    
    ## Create a temporary 'color_table.txt' file
    color_table=gscript.tempfile() # Define the csv output file name
    f = open(color_table, 'w')
    f.write(content)
    f.close()
    print "%s\n\nColor rule file saved in: '%s'"%(content,color_table)
    return color_table