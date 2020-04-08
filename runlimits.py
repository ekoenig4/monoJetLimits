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
    verbose = ["-v",str(args.verbose)]
    channels = [ card.replace('datacard_','') for card in os.listdir('../') if 'datacard' in card ]
    channels.sort(channel_order)
    sr_channel = [ channel for channel in channels if 'sr' in channel ]
    combine_cards = ['combineCards.py'] + ['%s=../datacard_%s' % (channel,channel) for channel in channels] + ['>','datacard']
    text2workspace = ['text2workspace.py','datacard','-m 1000']
    limits = ["combine","-M","AsymptoticLimits","-t","-1","-d","datacard.root","-m","1000"]
    collect = ["combineTool.py","-M","CollectLimits","higgsCombineTest.AsymptoticLimits.mH1000.root"]
    with open('run_limits.sh','w') as f:
        f.write("#!/bin/sh\n")
        f.write("set -e\n")
        f.write('set -o xtrace\n')
        f.write(' '.join(combine_cards)+'\n')
        f.write(' '.join(text2workspace)+'\n')
        f.write(' '.join(limits)+'\n')
        f.write(' '.join(collect)+'\n')
    proc = Popen(['sh','run_limits.sh','|','tee log']); proc.wait()
##############################################################################
def runDirectory(path,args):
    print path
    if 'nCR' in path: return
    cwd = os.getcwd()
    os.chdir(path)
    if not os.path.isdir('limits'): os.mkdir('limits')
    os.chdir('limits')
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
    parser.add_argument("-v","--verbose",help="Specify combine verbose level",type=int,default=0)
    try: args = parser.parse_args()
    except:
        parser.print_help()
        exit()
    return args
##############################################################################
if __name__ == "__main__":
    args = getargs()
    cwd = os.getcwd()
    for path in args.dir:
        os.chdir(cwd)
        runDirectory(path,args)
##############################################################################
