#!/usr/bin/env python
import os
from shutil import copyfile
import sys
from argparse import ArgumentParser
from subprocess import Popen,PIPE,STDOUT
from time import time
import json
import re

outdir_base = "/afs/hep.wisc.edu/home/ekoenig4/public_html/MonoZprimeJet/Plots%s/ExpectedLimits/"
def mvimpacts(sysdir):
    first = sysdir.split('_')[0]
    second = sysdir.split('_')[1]
    variable = re.findall('^.*[\+-]',first)
    if not any(variable): variable = first
    else: variable = variable[0][:-1]
    year = re.findall('\d\d\d\d',second)[0]
    outdir = outdir_base % year
    outname = 'impacts_%s.pdf' % sysdir.replace('.sys','')
    output = '%s/%s/%s' % (outdir,variable,outname)
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
    mvimpacts(sysdir)
#################################################################################################
