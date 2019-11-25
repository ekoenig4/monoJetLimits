#!/usr/bin/env python
import os
import sys
from argparse import ArgumentParser
import re
from subprocess import Popen,PIPE,STDOUT
from time import time
import json

class cPopen(Popen):
    def __init__(self,args,stdout=None,stderr=STDOUT):
        self.start = time()
        self.cwd = os.getcwd()
        self.args = args
        if stdout == None: super(cPopen,self).__init__(args)
        else:              super(cPopen,self).__init__(args,stdout=stdout,stderr=STDOUT)
    def duration(self): return time() - self.start
##############################################################################
def runMvdir(mx,mvdir,procmap=None):
    mv = mvdir.replace('Mv_','').replace('/','')
    cwd = os.getcwd()
    os.chdir(mvdir)
    combine = ['combine','-M','AsymptoticLimits','-n','Mx%sMv%s' % (mx,mv),'-m',mv,'workspace_Mv%s.root' % mv]
    if procmap is None:
        print os.getcwd()
        proc = cPopen(combine); proc.wait()
    else:
        proc = cPopen(combine,stdout=open('log','w'))
        procmap[os.getcwd()] = proc
    os.chdir(cwd)
##############################################################################
def runMxdir(mxdir,procmap=None):
    mx = mxdir.replace('Mx_','').replace('/','')
    cwd = os.getcwd()
    os.chdir(mxdir)
    mvdirs = [ dir for dir in os.listdir('.') if re.search(r'Mv_\d+$',dir) ]
    for mvdir in sorted(mvdirs): runMvdir(mx,mvdir,procmap)
    os.chdir(cwd)
##############################################################################
def runLimits(path,procmap=None):
    cwd = os.getcwd()
    os.chdir(path)
    mxdirs = [ dir for dir in os.listdir('.') if re.search(r'Mx_\d+$',dir) ]
    for mxdir in sorted(mxdirs): runMxdir(mxdir,procmap)
    os.chdir(cwd)
##############################################################################
def collectMxdir(mxdir,procmap=None):
    mx = mxdir.replace('Mx_','').replace('/','')
    cwd = os.getcwd()
    os.chdir(mxdir)
    output = 'zprimeMx%s.json' % mx
    args = ['combineTool.py','-M','CollectLimits']
    mvdirs = [ dir for dir in os.listdir('.') if re.search(r'Mv_\d+$',dir) ]
    combine_output = '%s/higgsCombineMx%sMv%s.AsymptoticLimits.mH%s.root'
    for mvdir in mvdirs:
        mv = mvdir.replace('Mv_','').replace('/','')
        args.append( combine_output % (mvdir,mx,mv,mv) )
    args += ['-o',output]
    if procmap is None:
        print cwd
        proc = cPopen(args); proc.wait()
    else:
        proc = cPopen(args,stdout=PIPE,stderr=STDOUT)
        procmap[os.getcwd()] = proc
    os.chdir(cwd)
##############################################################################
def collectLimits(path,procmap=None):
    cwd = os.getcwd()
    os.chdir(path)
    mxdirs = [ dir for dir in os.listdir('.') if re.search(r'Mx_\d+$',dir) ]
    for mxdir in sorted(mxdirs): collectMxdir(mxdir,procmap)
    os.chdir(cwd)
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
def collectWorkspaces(path,show=False):
    cwd = os.getcwd()
    os.chdir(path)
    mxdirs = [ dir for dir in os.listdir('.') if re.search(r'Mx_\d+$',dir) ]
    print 'Collecting %s' % path
    collectWorkspace(mxdirs,show=show)
    os.chdir(cwd)
##############################################################################
def runParallel():
    args = getargs()
    print 'Running Limits'
    if args.verbose: procmap=None
    else:         procmap={}
    for path in args.dir: runLimits(path,procmap)
    printProcs(procmap,'Mx Limits')
    print 'Collecting Limits'
    for path in args.dir: collectLimits(path,procmap)
    printProcs(procmap,'Mx Output')
    for path in args.dir: collectWorkspaces(path,show=args.verbose)
##############################################################################
def runSerial():
    args = getargs()
    for path in args.dir:
        print 'Running Limits',path
        if args.verbose: procmap=None
        else:         procmap={}
        # runLimits(path,procmap)
        printProcs(procmap,'Mx Limits')
        print 'Collecting Limits'
        collectLimits(path,procmap)
        printProcs(procmap,'Mx Output')
        collectWorkspaces(path,show=args.verbose)
##############################################################################
def getargs():
    def directory(arg):
        if os.path.isdir(arg): return arg
        else: raise ValueError()
    parser = ArgumentParser(description='Run all avaiable limits in specified directory')
    parser.add_argument("-d","--dir",help='Specify the directory to run limits in',action='store',type=directory,default=None,nargs='+',required=True)
    parser.add_argument("-v","--verbose",help='Show output from combine',action='store_true',default=False)
    # parser.add_argument("-r","--reset",help='Run limits event if they have already been done',action='store_true',default=False)
    try: args = parser.parse_args()
    except:
        parser.print_help()
        exit()
    return args
##############################################################################
if __name__ == "__main__": runSerial()
#################################################################################################
