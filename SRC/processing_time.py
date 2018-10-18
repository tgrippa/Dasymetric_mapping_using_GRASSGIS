#!/usr/bin/env python

"""
Functions to manage and inform the user about processing time used.
The print_processing_time(begintime, printmessage) is used to calculate and display the processing time for various stages of the processing chain. 
At the beginning of each major step, the current time is stored in a new variable, using start_processing() function. 
At the end of the stage in question, the print_processing_time(begintime, printmessage) function is called and takes as argument the variable 
containing the recorded time at the beginning of the stage, and an output message.
"""

## Import library for managing time in python
import time  


def start_processing():    
    return time.time()
    
def print_processing_time(begintime, printmessage):    
    ## Function "print_processing_time()" compute processing time and printing it.
    # The argument "begintime" wait for a variable containing the begintime (result of time.time()) of the process for which to compute processing time.
    # The argument "printmessage" wait for a string format with information about the process. 
    endtime=time.time()           
    processtime=endtime-begintime
    remainingtime=processtime

    days=int((remainingtime)/86400)
    remainingtime-=(days*86400)
    hours=int((remainingtime)/3600)
    remainingtime-=(hours*3600)
    minutes=int((remainingtime)/60)
    remainingtime-=(minutes*60)
    seconds=round((remainingtime)%60,1)

    if processtime<60:
        finalprintmessage=str(printmessage)+str(seconds)+" seconds"
    elif processtime<3600:
        finalprintmessage=str(printmessage)+str(minutes)+" minutes and "+str(seconds)+" seconds"
    elif processtime<86400:
        finalprintmessage=str(printmessage)+str(hours)+" hours and "+str(minutes)+" minutes and "+str(seconds)+" seconds"
    elif processtime>=86400:
        finalprintmessage=str(printmessage)+str(days)+" days, "+str(hours)+" hours and "+str(minutes)+" minutes and "+str(seconds)+" seconds"
    
    return finalprintmessage