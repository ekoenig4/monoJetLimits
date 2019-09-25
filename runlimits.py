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
    print 'Collecting Workspace'
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
def collectMxdir(mxdir,show=False):
    mx = mxdir.replace('Mx_','').replace('/','')
    cwd = os.getcwd()
    os.chdir(mxdir)
    with open('mvlist','r') as f: mvlist = f.readlines()
    mxdict = {}
    mvprocs = []
    output = 'zprimeMx%s.json' % mx
    if not os.path.isfile(output):
        args = ['combineTool.py','-M','CollectLimits']
        for mv in mvlist:
            mv = mv.replace('\n','')
            args.append( 'higgsCombineMx%s_Mv%s.AsymptoticLimits.mH%s.root' % (mx,mv,mv) )
        args += ['-o',output]
        if show:
            mxproc = cPopen(args)
            proc.wait()
        else:
            mxproc = cPopen(args,stdout=PIPE,stderr=STDOUT)
        mxdict[mx] = mxproc
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
            print 'Mx %s Mv %s' % (mx,mv)
            proc = cPopen(args)
            proc.wait()
        else:
            proc = cPopen(args,stdout=PIPE,stderr=STDOUT)
            mvprocs['Mx%sMv%s' % (mx,mv)] = proc
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
    out = '%s : %i%%\n' % (prompt,100)
    sys.stdout.write(out)
    sys.stdout.flush()
##############################################################################
def getargs():
    def directory(arg):
        if os.path.isdir(arg): return arg
        else: raise ValueError()
    parser = ArgumentParser(description='Run all avaiable limits in specified directory')
    parser.add_argument("-d","--dir",help='Specify the directory to run limits in',action='store',type=directory,default=None,required=True)
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
    mxdirs = [ dir for dir in os.listdir('.') if re.search(r'Mx_\d+$',dir) ]
    procs = {}
    print 'Running Limits'
    for mxdir in sorted(mxdirs): procs.update( runMxdir(mxdir,show=args.verbose,show=args.reset) )
    printProcs(procs,'Mx Limits')
    print 'Collecting Limits'
    for mxdir in sorted(mxdirs): procs.update( collectMxdir(mxdir,show=args.verbose) )
    printProcs(procs,'Mx Output')
    collectWorkspace(mxdirs,show=args.verbose)
#################################################################################################
