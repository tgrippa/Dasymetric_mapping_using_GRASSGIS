#!/usr/bin/env python

"""
Function that apply a color scheme on a raster. 
Takes a KEY=VALUE dictionnary as input with pixel value as KEY and color (R:G:B) as VALUE
"""

import grass.script as gscript

def create_color_rule(color_dict):
	# Define color table. Replace with the RGB values of wanted colors of each class
	content="\n".join(["%s %s"%(key,color_dict[key]) for key in color_dict.keys()])
	
	## Create a temporary 'color_table.txt' file
	color_table=gscript.tempfile() # Define the csv output file name
	f = open(color_table, 'w')
	f.write(content)
	f.close()
	print "Color rule: \n%s\nSaved in file: '%s'"%(content,color_table)
	return color_table