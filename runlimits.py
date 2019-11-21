#!/usr/bin/env python
import os
import sys
from argparse import ArgumentParser
import re
from subprocess import Popen,PIPE,STDOUT
from time import time
import json

class cPopen(Popen):
    def __init__(self,*args,**kwargs):
        self.start = time()
        super(cPopen,self).__init__(*args,**kwargs)
    def duration(self): return time() - self.start
##############################################################################
def collectWorkspace(mxdirs,show=False):
    with open('signal_scaling.json') as f: scaling = json.load(f)
    mxjsons = {}
    cwd = os.getcwd()
    for mxdir in mxdirs:
        mx = mxdir.replace('Mx_','').replace('/','')
        with open('Mx_%s/zprimeMx%s.json' % (mx,mx)) as f: mxjsons[mx] = json.load(f)
    #####
    ws = {}
    for mx,mxjson in mxjsons.iteritems():
        mx_ws = {}
        for mv in mxjson:
            mv_ws = {}
            lim = mxjson[mv]
            mv = str(int(float(mv)))
            key = 'Mx%s_Mv%s' % (mx,mv)
            scale = scaling[key] if key in scaling else 1
            mv_ws['scale'] = scale
            mv_ws['limits'] = lim
            mx_ws[mv] = mv_ws
        ws[mx] = mx_ws
    #####
    with open('limits.json','w') as f: json.dump(ws,f,indent=4)
##############################################################################
def collectMxdir(mxdir,show=False,reset=False):
    mx = mxdir.replace('Mx_','').replace('/','')
    cwd = os.getcwd()
    os.chdir(mxdir)
    with open('mvlist','r') as f: mvlist = f.readlines()
    mxdict = {}
    mvprocs = []
    output = 'zprimeMx%s.json' % mx
    if not os.path.isfile(output) or reset:
        args = ['combineTool.py','-M','CollectLimits']
        for mv in mvlist:
            mv = mv.replace('\n','')
            args.append( 'higgsCombineMx%s_Mv%s.AsymptoticLimits.mH%s.root' % (mx,mv,mv) )
        args += ['-o',output]
        if show:
            print cwd,mxdir
            mxproc = cPopen(args)
            mxproc.wait()
        else:
            mxproc = cPopen(args,stdout=PIPE,stderr=STDOUT)
        mxdict['%s_%s' % (cwd,mx)] = mxproc
    #####
    os.chdir(cwd)
    return mxdict
##############################################################################
def runMxdir(mxdir,show=False,reset=False):
    mx = mxdir.replace('Mx_','').replace('/','')
    cwd = os.getcwd()
    os.chdir(mxdir)
    with open('mvlist','r') as f: mvlist = f.readlines()
    mvprocs = {}
    for mv in mvlist:
        mv = mv.replace('\n','')
        output = 'higgsCombineMx%s_Mv%s.AsymptoticLimits.mH%s.root' % (mx,mv,mv)
        if not reset and os.path.isfile(output): continue
        args =  [ 'combine','-M','AsymptoticLimits','-n','Mx%s_Mv%s' % (mx,mv),'-m',mv,'datacard' ]
        if show:
            print cwd,mxdir,mv
            proc = cPopen(args)
            proc.wait()
        else:
            proc = cPopen(args,stdout=PIPE,stderr=STDOUT)
            mvprocs['%s_Mx%sMv%s' % (cwd,mx,mv)] = proc
    os.chdir(cwd)
    return mvprocs
##############################################################################
def printProcs(procs,name):
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
def runLimits(path,show=False,reset=False):
    cwd = os.getcwd()
    os.chdir(path)
    mxdirs = [ dir for dir in os.listdir('.') if re.search(r'Mx_\d+$',dir) ]
    procs = {}
    for mxdir in sorted(mxdirs):
        procs.update( runMxdir(mxdir,show,reset) )
    os.chdir(cwd)
    return procs
##############################################################################
def collectLimits(path,show=False,reset=False):
    cwd = os.getcwd()
    os.chdir(path)
    mxdirs = [ dir for dir in os.listdir('.') if re.search(r'Mx_\d+$',dir) ]
    procs = {}
    for mxdir in sorted(mxdirs):
        procs.update( collectMxdir(mxdir,show,reset) )
    os.chdir(cwd)
    return procs
##############################################################################
def collectWorkspaces(path,show=False):
    cwd = os.getcwd()
    os.chdir(path)
    mxdirs = [ dir for dir in os.listdir('.') if re.search(r'Mx_\d+$',dir) ]
    print 'Collecting %s' % path
    collectWorkspace(mxdirs,show=show)
    os.chdir(cwd)
##############################################################################
def getargs():
    def directory(arg):
        if os.path.isdir(arg): return arg
        else: raise ValueError()
    parser = ArgumentParser(description='Run all avaiable limits in specified directory')
    parser.add_argument("-d","--dir",help='Specify the directory to run limits in',action='store',type=directory,default=None,nargs='+',required=True)
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
    print 'Running Limits'
    procs = {}
    for path in args.dir: procs.update( runLimits(path,show=args.verbose,reset=args.reset) )
    printProcs(procs,'Mx Limits')
    print 'Collecting Limits'
    for path in args.dir: procs.update( collectLimits(path,show=args.verbose,reset=args.reset) )
    printProcs(procs,'Mx Output')
    for path in args.dir: collectWorkspaces(path,show=args.verbose)
#################################################################################################
