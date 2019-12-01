#!/usr/bin/env python
import os
from shutil import copyfile
import sys
from argparse import ArgumentParser
from subprocess import Popen,PIPE,STDOUT
from time import time
import json
import re
from ROOT import *

def runFit(args):
    if os.path.isfile('fitDiagnostics_fit_CRonly_result.root') and not args.reset: return
    combine_cards = ['combineCards.py','sr=../datacard_sr']
    for cr in ('e','ee','m','mm'): combine_cards.append('%s=../datacard_%s' % (cr,cr))
    combine_cards += ['>','datacard']
    text2workspace = ['text2workspace.py','datacard','--channel-masks']
    cr_only_fit = ["combine","-M","FitDiagnostics","-d","datacard.root","-n","_fit_CRonly_result","--saveShapes","--saveWithUncertainties","--setParameters","mask_sr=1"]
    with open('run_cr_only_fit.sh','w') as f:
        f.write("#!/bin/sh\n")
        f.write(' '.join(combine_cards)+'\n')
        f.write(' '.join(text2workspace)+'\n')
        f.write(' '.join(cr_only_fit)+'\n')
    proc = Popen(['sh','run_cr_only_fit.sh']); proc.wait()
##############################################################################
def runDirectory(path,args):
    print path
    if 'nCR' in path: return
    cwd = os.getcwd()
    os.chdir(path)
    if not os.path.isdir('cr_fit'): os.mkdir('cr_fit')
    os.chdir('cr_fit')
    runFit(args)
    os.chdir(cwd)
##############################################################################
def getargs():
    def directory(arg):
        if os.path.isdir(arg): return arg
        raise ValueError()
    def signal(arg):
        regex = re.compile(r"Mx\d*_Mv\d*$")
        if regex.match(arg): return arg
        raise ValueError()
    parser = ArgumentParser(description='Run all avaiable limits in specified directory')
    parser.add_argument("-d","--dir",help='Specify the directory to run limits in',nargs='+',action='store',type=directory,required=True)
    parser.add_argument("-r","--reset",help='Rerun combine fit diagnositics',action='store_true',default=False)
    try: args = parser.parse_args()
    except:
        parser.print_help()
        exit()
    return args
##############################################################################
if __name__ == "__main__":
    args = getargs()
    for path in args.dir: runDirectory(path,args)
##############################################################################
