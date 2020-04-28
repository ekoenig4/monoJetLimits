#!/usr/bin/env python
import os
from shutil import copyfile
import sys
sys.path.append('PlotTool')
from PlotTool import SysInfo
from argparse import ArgumentParser
from subprocess import Popen,PIPE,STDOUT
from time import time
import json
import re

outdir_base = "/afs/hep.wisc.edu/home/ekoenig4/public_html/MonoJet/Plots%s/ExpectedLimits/"

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
##############################################################################
def printProcs(procs,name):
    if procs is None: return
    cutoff = 300 # seconds
    prompt = '{0:<22}'.format( '\rProcessing %i %s' % (len(procs),name) )
    total = len(procs)
    current = total
    out = '%s : %i%%' % (prompt,0)
    sys.stdout.write(out)
    sys.stdout.flush()
    while any(procs):
        IDlist = procs.keys()
        for ID in IDlist:
            if procs[ID].poll() != None:
                procs.pop(ID)
            # elif procs[ID].duration() > cutoff:
            #     procs[ID].terminate()
            #     procs.pop(ID)
        ##################################################
        if current != len(procs):
            current = len(procs)
            percent = 100 * (total - current)/float(total)
            out = '%s : %.3f%%' % (prompt,percent)
            sys.stdout.write(out)
            sys.stdout.flush()
    out = '%s : %.3f%%\n' % (prompt,100.)
    sys.stdout.write(out)
    sys.stdout.flush()
##############################################################################
def mvimpacts(path):
    cwd = os.getcwd()
    info = SysInfo(path)
    os.chdir(path)
    output = info.getOutputDir(outdir_base)
    if not os.path.isfile('impacts/impacts.pdf'): return
    if not os.path.isdir(output): os.makedirs(output)
    outname = 'impacts_%s.pdf' % info.sysdir
    print 'Moving impacts/impacts.pdf to %s/%s' % (output,outname)
    copyfile('impacts/impacts.pdf',"%s/%s" % (output,outname))
    os.chdir(cwd)
##############################################################################
def runImpacts(path,mx,mv,procmap=None,strength=0.0,verbose=0,reset=False):
    cwd = os.getcwd()
    os.chdir(path)
    if not os.path.isdir('impacts'): os.mkdir('impacts')
    os.chdir('impacts')
    if reset: os.system("rm *")

    #--- Combine Cards and Mask SR ---#
    verbose = ["-v",str(verbose)]
    channels = [ card.replace('datacard_','') for card in os.listdir('../') if 'datacard' in card ]
    channels.sort(channel_order)
    sr_channel = [ channel for channel in channels ]
    combine_cards = ['combineCards.py'] + ['%s=../datacard_%s' % (channel,channel) for channel in channels] + ['>','datacard']
    text2workspace = ['text2workspace.py','datacard','-m',mv,'-o','Mchi%s_Mphi%s.root' % (mx,mv)]

    workspace = ["-d",'Mchi%s_Mphi%s.root' % (mx,mv),"-m",mv]
    common_opts = ["-t -1 --expectSignal=%.1f --parallel=24 --rMin=-1 --autoRange 5 --squareDistPoiStep"%strength]+verbose
    impacts = ["combineTool.py","-M","Impacts"]
    initial_fit = ["--doInitialFit","--robustFit 1"]
    do_fit = ["--robustFit 1","--doFits"]
    output = ["-o","impacts.json"]
    plot = ["plotImpacts.py","-i","impacts.json","-o","impacts"]
    log = [">>log"]

    tag = "task_Mchi%s_Mphi%s" % (mx,mv)
    condor = ["--job-mode","condor","--task-name",tag]
    condor_wait = ["condor_wait","%s*.log"%tag,"|","exit $?"]
    com = ['#']

    combine_1 = impacts + workspace + initial_fit + common_opts + log
    combine_2 = impacts + workspace + do_fit + common_opts + log 
    combine_3 = impacts + workspace + output + common_opts + log
    #--- Combine Impact Commands ---#
    with open('run_impacts.sh','w') as f:
        f.write('set -e\n')
        f.write('set -o xtrace\n')
        f.write(' '.join(combine_cards)+'\n')
        f.write(' '.join(text2workspace)+'\n')
        f.write(' '.join(combine_1)+'\n')
        f.write(' '.join(combine_2)+'\n')
        f.write(' '.join(combine_3)+'\n')
        f.write(' '.join(plot)+'\n')
    command = ['sh','run_impacts.sh']
    if procmap is None:
        print os.getcwd()
        proc = Popen(command); proc.wait()
    else:
        proc = Popen(command,stdout=open('log','w'),stderr=STDOUT)
        procmap[os.getcwd()] = proc
    os.chdir(cwd)
##############################################################################
def runParallel(args=None):
    if args is None: args = getargs()
    args.dir = [ path for path in args.dir if not ('nSYS' in path and 'nSTAT' in path) ]
    print 'Running Impacts'
    mx,mv = "1","1000"
    procmap = {}
    for path in args.dir: runImpacts(path,mx,mv,procmap,verbose=args.verbose,reset=args.reset)
    printProcs(procmap,'Impacts')
    for path in args.dir: mvimpacts(path)
##############################################################################
def runSerial(args=None):
    if args is None: args = getargs()
    args.dir = [ path for path in args.dir if not ('nSYS' in path and 'nSTAT' in path) ]
    print 'Running Impacts'
    mx,mv = "1","1000"
    cwd = os.getcwd()
    for path in args.dir:
        os.chdir(cwd)
        runImpacts(path,mx,mv,verbose=args.verbose,reset=args.reset)
        mvimpacts(path)
##############################################################################
def getargs():
    def directory(arg):
        if os.path.isdir(arg): return arg
        raise ValueError()
    parser = ArgumentParser(description='Run all avaiable limits in specified directory')
    parser.add_argument("-d","--dir",help='Specify the directory to run limits in',nargs='+',action='store',type=directory,required=True)
    parser.add_argument("-r","--reset",help="Rerun impacts",action="store_true")
    parser.add_argument("-s","--signal",help='Specify the signal strength',action='store',type=float,default=0.0)
    parser.add_argument("-p","--parallel",help="Run all directories in parallel",action='store_true',default=False)
    parser.add_argument("-v","--verbose",help="Specify combine verbose level",type=int,default=0)
    
    try: args = parser.parse_args()
    except:
        parser.print_help()
        exit()
    return args
##############################################################################
if __name__ == "__main__":
    args = getargs()
    if not args.parallel: runSerial(args)
    else: runParallel(args)
#################################################################################################
