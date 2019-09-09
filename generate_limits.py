from ROOT import *
import os
from optparse import OptionParser
from array import array
from makeCards import makeCards,GetMasses
import re

######################################################################
if __name__ == "__main__":
    if not os.path.isdir("Limits/"): os.mkdir("Limits/")
    
    parser = OptionParser()
    parser.add_option("-i","--input",help="Specify input systematics file to generate limits from",action="store",type="str",default=None)
    options,args = parser.parse_args()
    
    masses = GetMasses(options.input)
    sysfile = os.getcwd() + '/' + options.input
    fname = options.input.split('/')[-1]
    ##########################################################
    dir = 'Limits/'+fname.replace('.root', '')
    if not os.path.isdir(dir): os.mkdir(dir)
    ##################################################
    os.chdir(dir)
    makeCards(sysfile,masses)
