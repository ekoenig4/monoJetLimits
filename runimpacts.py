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
def mvimpacts(info):
    outdir = outdir_base % info.year
    outname = 'impacts_%s.pdf' % info.sysdir
    output = '%s/%s/%s' % (outdir,info.variable,info.sysdir,outname)
    if not os.path.isfile('impacts/impacts.pdf'): return
    print 'Moving impacts/impacts.pdf to %s' % output
    copyfile('impacts/impacts.pdf',output)
##############################################################################
def runImpacts(signal,scale,mv,impactdir):
    os.chdir(impactdir)
    blind = ['-t','-1','--expectSignal','1']
    impacts = ['combineTool.py','-M','Impacts']
    card = ['-m',mv,'-d','%s.root' % signal]

    def run(command):
        print ' '.join(command)
        proc = Popen(command)
        proc.wait()
    run(impacts + card + blind + ['--doInitialFit'])
    run(impacts + card + blind + ['--allPars','--doFits','--parallel','12'])
    run(impacts + card + ['--allPars','-o','impacts.json'])
    run(['plotImpacts.py','-i','impacts.json','-o','impacts'])
##############################################################################
def getText2WS(mxdir,mv,signal):
    print 'Text2Workspace'
    args = ['text2workspace.py','%s/datacard' % mxdir,'-m',mv,'-o','impacts/%s.root' % signal]
    proc = Popen(args)
    proc.wait()
##############################################################################
def runDirectory(path,args):
    print path
    info = SysInfo(path)
    home = os.getcwd()
    os.chdir(path)
    cwd = os.getcwd()
    with open('signal_scaling.json') as f: scaling = json.load(f)
    scale = 1/float(scaling[args.signal])
    sysdir = next( sub for sub in cwd.split('/') if '.sys' in sub )
    mx = args.signal.split('_')[0].replace('Mx','')
    mxdir = 'Mx_%s' % mx
    mv = args.signal.split('_')[1].replace('Mv','')
    impactdir = 'impacts'
    if not os.path.isdir(impactdir): os.mkdir(impactdir)
    else:                            os.system('rm impacts/*')
    impactdir = os.path.abspath(impactdir)
    getText2WS(mxdir,mv,args.signal)
    runImpacts(args.signal,scale,mv,impactdir)
    os.chdir(cwd)
    mvimpacts(info)
    os.chdir(home)
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
    parser.add_argument("-s","--signal",help='Specify the signal (Mxd_Mvd) sample to get impact for',action='store',type=signal,required=True)
    try: args = parser.parse_args()
    except:
        parser.print_help()
        exit()
    return args
##############################################################################
if __name__ == "__main__":
    args = getargs()
    for path in args.dir: runDirectory(path,args)
#################################################################################################
