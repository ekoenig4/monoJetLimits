from ROOT import *
import os
from optparse import OptionParser
from array import array
import re



if __name__ == "__main__":
    parser = OptionParser()
    parser.add_option("-i","--input",help="Specify input systematics file to generate limits from",action="store",type="str",default=None)
    options,args = parser.parse_args()

    GetTransferFactors(options.input)


