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

outdir_base = "/afs/hep.wisc.edu/home/ekoenig4/public_html/MonoZprimeJet/Plots%s/ExpectedLimits/"
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
    outdir = outdir_base % info.year
    outname = 'impacts_%s.pdf' % info.sysdir
    output = '%s/%s/%s/%s' % (outdir,info.variable,info.sysdir,outname)
    if not os.path.isfile('impacts/impacts.pdf'): return
    print 'Moving impacts/impacts.pdf to %s' % output
    copyfile('impacts/impacts.pdf',output)
    os.chdir(cwd)
##############################################################################
def runImpacts(path,mx,mv,procmap=None):
    cwd = os.getcwd()
    os.chdir(path)
    os.chdir('impacts')
    blind = ['-t','-1','--expectSignal','1']
    impacts = ['combineTool.py','-M','Impacts']
    card = ['-m',mv,'-d','Mchi%s_Mphi%s.root' % (mx,mv)]

    c1 = ' '.join(impacts + card + blind + ['--doInitialFit'])+'>>log'
    c2 = ' '.join(impacts + card + blind + ['--allPars','--doFits','--parallel 12'])+' >>log'
    c3 = ' '.join(impacts + card + ['--allPars','-o','impacts.json'])+'>>log'
    c4 = ' '.join(['plotImpacts.py','-i','impacts.json','-o','impacts'])+'>>log'
    with open('run_impacts.sh','w') as f:
        f.write('set -o xtrace\n')
        f.write('\n'.join([c1,c2,c3,c4]))
    command = ['sh','run_impacts.sh']
    if procmap is None:
        print os.getcwd()
        proc = Popen(command); proc.wait()
    else:
        proc = Popen(command,stdout=open('log','w'),stderr=STDOUT)
        procmap[os.getcwd()] = proc
    os.chdir(cwd)
##############################################################################
def getText2WS(path,mx,mv,procmap=None):
    cwd = os.getcwd()
    os.chdir(path)
    if not os.path.isdir('impacts'): os.mkdir('impacts')
    command = ['text2workspace.py','Mchi_%s/datacard' % mx,'-m',mv,'-o','impacts/Mchi%s_Mphi%s.root' % (mx,mv)]
    if procmap is None:
        print os.getcwd()
        proc = Popen(command); proc.wait()
    else:
        proc = Popen(command,stdout=PIPE,stderr=STDOUT)
        procmap[os.getcwd()] = proc
    os.chdir(cwd)
##############################################################################
def runParallel(args=None):
    if args is None: args = getargs()
    args.dir = [ path for path in args.dir if not ('nSYS' in path and 'nSTAT' in path) ]
    print 'Running Impacts'
    mx,mv = args.signal.replace('Mchi',"").replace("Mphi","").split('_')
    procmap = {}
    for path in args.dir: getText2WS(path,mx,mv,procmap)
    printProcs(procmap,'Text2Workspace')
    for path in args.dir: runImpacts(path,mx,mv,procmap)
    printProcs(procmap,'Impacts')
    for path in args.dir: mvimpacts(path)
##############################################################################
def runSerial(args=None):
    if args is None: args = getargs()
    args.dir = [ path for path in args.dir if not ('nSYS' in path and 'nSTAT' in path) ]
    print 'Running Impacts'
    mx,mv = args.signal.strip('Mchi').strip('Mphi').split('_')
    for path in args.dir:
        getText2WS(path,mx,mv)
        runImpacts(path,mx,mv)
        mvimpacts(path)
##############################################################################
def runDirectory(path,args):
    print path
    if 'nSYS' in path and 'nSTAT' in path: return
    info = SysInfo(path)
    home = os.getcwd()
    os.chdir(path)
    cwd = os.getcwd()
    scaling = {}
    if os.path.isfile('../signal_scaling.json'):
        with open('../signal_scaling.json') as f: scaling = json.load(f)
    scale = 1/float(scaling[args.signal]) if args.signal in scaling else 1
    sysdir = next( sub for sub in cwd.split('/') if '.sys' in sub )
    mx = args.signal.split('_')[0].replace('Mchi','')
    mxdir = 'Mchi_%s' % mx
    mv = args.signal.split('_')[1].replace('Mphi','')
    impactdir = 'impacts'
    if not os.path.isdir(impactdir): os.mkdir(impactdir)
    else:                            os.system('rm impacts/*')
    impactdir = os.path.abspath(impactdir)
    getText2WS(mxdir,mv,args.signal)
    runImpacts(args.signal,scale,mv,impactdir)
    mvimpacts(info)
    os.chdir(home)
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
    parser.add_argument("-s","--signal",help='Specify the signal (Mchid_Mphid) sample to get impact for',action='store',type=signal,default="Mchi1_Mphi1000")
    parser.add_argument("-p","--parallel",help="Run all directories in parallel",action='store_true',default=False)
    
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
