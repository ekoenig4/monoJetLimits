import os
from shutil import copyfile
import sys
from argparse import ArgumentParser
from subprocess import Popen,PIPE,STDOUT
from time import time
import json
import re
from ROOT import *
from PlotTool import *


def getargs():
    parser = ArgumentParser()
    parser.add_argument("-w","--workspace",type=TFile)
    try: args = parser.parse_args()
    except:
        parser.print_help()
        exit()
    return args
##############################################################################

if __name__ == "__main__":

    args = getargs()
    ws = args.workspace.Get("w")

    obs = ws.allVars().first()
    obset = RooArgSet(obs)
    pdfs = [ pdf for pdf in setiter(ws.allPdfs()) ]

    zjets_sr = pdfs[0]
    for param in setiter( zjets_sr.getParameters(obset) ): param.setVal(1.0)

    proc = pdfs[2]
    proc_bins = ws.allFunctions().selectByName(proc.GetName()+"_bin*")
    proc_fr_bins = ws.allFunctions().selectByName("func_r_"+proc.GetName()+"_bin*")
    proc_vr_bins = ws.allVars().selectByName("r_"+proc.GetName()+"_bin*")

    proc.Print()
    for fbin in setiter(proc_vr_bins): fbin.Print()
    # for fbin in setiter(proc_bins): fbin.Print()
    # for param in setiter( proc.getParameters(obset) ):param.Print()
