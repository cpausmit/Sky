#---------------------------------------------------------------------------------------------------
# Python Module File to describe a power spectrum
#
# Author: C.Paus                                                                      (May 11, 2022)
#---------------------------------------------------------------------------------------------------

DEBUG = 0

#---------------------------------------------------------------------------------------------------
"""
Class:  Power_spectrum(tag,config,version,sw,dataset,dbs,jobFile,siteFile)
Each task in condor is described in this class
"""
#---------------------------------------------------------------------------------------------------
class Power_spectrum:
    "Description of a Power_spectrum"

    #-----------------------------------------------------------------------------------------------
    # constructor for new creation
    #-----------------------------------------------------------------------------------------------
    def __init__(self,tag,frequencies,powers):
        self.tag = tag
        self.frequencies = frequencies
        self.powers = powers

    #-----------------------------------------------------------------------------------------------
    # dump the power spectrum into a file_handle
    #-----------------------------------------------------------------------------------------------
    def write(self,file_handle):
        return

    #-----------------------------------------------------------------------------------------------
    # read the power spectrum from a file_handle
    #-----------------------------------------------------------------------------------------------
    def write(self,file_handle):
        return

    #-----------------------------------------------------------------------------------------------
    # present the power spectrum
    #-----------------------------------------------------------------------------------------------
    def show(self):
        print(' ====  P o w e r  S p e c t r u m  ====')
        print(' ')
        print(' Tag          : ' + self.tag)
        print(' Frequencies')
        print(self.frequencies)
        print(' Powers')
        print(self.powers)
