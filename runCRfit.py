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

ch_order = ('sr','we','wm','ze','zm','ga')

def channel_order(ch1,ch2):
    for i,ch in enumerate(ch_order):
        if ch in ch1: i1 = i
        if ch in ch2: i2 = i
    if i1 < i2: return -1
    elif i1 == i2:
            y1 = re.findall('\d\d\d\d',ch1)
            y2 = re.findall('\d\d\d\d',ch2)
            if any(y1) and any(y2):
                y1 = int(y1[0]); y2 = int(y2[0])
                if y1 < y2: return -1
    return 1

def runFit(args):
    if os.path.isfile('fitDiagnostics_fit_CRonly_result.root') and not args.reset: return
    channels = [ card.replace('datacard_','') for card in os.listdir('../') if 'datacard' in card ]
    channels.sort(channel_order)
    sr_channel = [ channel for channel in channels if 'sr' in channel ]
    combine_cards = ['combineCards.py'] + ['%s=../datacard_%s' % (channel,channel) for channel in channels] + ['>','datacard']
    text2workspace = ['text2workspace.py','datacard','--channel-masks']
    cr_only_fit = ["combine","-M","FitDiagnostics","-d","datacard.root","-n","_fit_CRonly_result","--saveShapes","--saveWithUncertainties","--robustFit 1"]
    cr_only_fit += ["--setParameters",','.join(['mask_%s=1' % channel for channel in sr_channel])]
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
        regex = re.compile(r"Mchi\d*_Mphi\d*$")
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
