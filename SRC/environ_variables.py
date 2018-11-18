#!/usr/bin/env python

"""
Functions related to environmental variables
"""

import os,sys

def setup_environmental_variables():
	"""	Setting the environment variables allowing to use of GRASS GIS python libraries 
	Documentaion available on: https://grass.osgeo.org/grass64/manuals/variables.html
	Please change the directory path according to your own system configuration.
	Here after are the path used on a LINUX UBUNTU Mint 18.1 (Serena).
    """
	# Check is environmental variables exists and create them (empty) if not exists.
	if not 'PYTHONPATH' in os.environ:
		os.environ['PYTHONPATH']=''
	if not 'LD_LIBRARY_PATH' in os.environ:
		os.environ['LD_LIBRARY_PATH']=''
	# Set environmental variables
	os.environ['GISBASE'] = '/home/tais/SRC/GRASS/grass_trunk/dist.x86_64-pc-linux-gnu'
	os.environ['PATH'] += os.pathsep + os.path.join(os.environ['GISBASE'],'bin')
	os.environ['PATH'] += os.pathsep + os.path.join(os.environ['GISBASE'],'script')
	os.environ['PATH'] += os.pathsep + os.path.join(os.environ['GISBASE'],'lib')
	#os.environ['PATH'] += os.pathsep + os.path.join(os.environ['GISBASE'],'etc','python')
	os.environ['PYTHONPATH'] += os.pathsep + os.path.join(os.environ['GISBASE'],'etc','python')
	os.environ['PYTHONPATH'] += os.pathsep + os.path.join(os.environ['GISBASE'],'etc','python','grass')
	os.environ['PYTHONPATH'] += os.pathsep + os.path.join(os.environ['GISBASE'],'etc','python','grass','script')
	os.environ['PYTHONLIB'] = '/usr/lib/python2.7'
	os.environ['LD_LIBRARY_PATH'] += os.pathsep + os.path.join(os.environ['GISBASE'],'lib')
	os.environ['GIS_LOCK'] = '$$'
	os.environ['GISRC'] = os.path.join(os.environ['HOME'],'.grass7','rc')

	## Define GRASS-Python environment
	sys.path.append(os.path.join(os.environ['GISBASE'],'etc','python'))


def print_environmental_variables():
	"""
	Display the current environmental variables of your computer.
	"""
	## Display the current defined environment variables
	for key in os.environ.keys():
		print "%s = %s \t" % (key,os.environ[key])