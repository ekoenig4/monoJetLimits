#!/usr/bin/env python
import os
import sys
from argparse import ArgumentParser
import re
from subprocess import Popen,PIPE,STDOUT
from time import time
import json

def runImpacts(signal,mv,impactdir):
    os.chdir(impactdir)
    args = ['combineTool.py','-M','Impacts','-m',mv,'-d','%s.root' % signal]
    print args + ['--doInitialFit']
    proc = Popen(args + ['--doInitialFit'])
    proc.wait()
    print args + ['--allPars','--doFits','--parallel','12']
    proc = Popen(args + ['--allPars','--doFits','--parallel','12'])
    proc.wait()
    print args + ['--allPars','-o','impacts.json']
    proc = Popen(args + ['--allPars','-o','impacts.json'])
    proc.wait()
    print ['plotImpacts.py','-i','impacts.json','-o','impacts']
    proc = Popen(['plotImpacts.py','-i','impacts.json','-o','impacts'])
    proc.wait()
##############################################################################
def getText2WS(mxdir,mv,signal):
    print 'Text2Workspace'
    args = ['text2workspace.py','%s/datacard' % mxdir,'-m',mv,'-o','impacts/%s.root' % signal]
    proc = Popen(args)
    proc.wait()
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
    parser.add_argument("-d","--dir",help='Specify the directory to run limits in',action='store',type=directory,required=True)
    parser.add_argument("-s","--signal",help='Specify the signal (Mxd_Mvd) sample to get impact for',action='store',type=signal,required=True)
    parser.add_argument("-v","--verbose",help='Show output from combine',action='store_true',default=False)
    parser.add_argument("-r","--reset",help='Run limits event if they have already been done',action='store_true',default=False)
    try: args = parser.parse_args()
    except:
        parser.print_help()
        exit()
    return args
##############################################################################
if __name__ == "__main__":
    args = getargs()
    os.chdir(args.dir)
    cwd = os.getcwd()
    mx = args.signal.split('_')[0].replace('Mx','')
    mxdir = 'Mx_%s' % mx
    mv = args.signal.split('_')[1].replace('Mv','')
    impactdir = 'impacts'
    if not os.path.isdir(impactdir): os.mkdir(impactdir)
    impactdir = os.path.abspath(impactdir)
    getText2WS(mxdir,mv,args.signal)
    runImpacts(args.signal,mv,impactdir)
#################################################################################################
