#!/usr/bin/env python
import os
import sys
from optparse import OptionParser
import re
from subprocess import Popen,PIPE,STDOUT
from time import time

class cPopen(Popen):
    def __init__(self,*args,**kwargs):
        self.start = time()
        super(cPopen,self).__init__(*args,**kwargs)
    def duration(self): return time() - self.start
##############################################################################
def collectMxdir(mxdir,show=False):
    mx = mxdir.replace('Mx_','').replace('/','')
    cwd = os.getcwd()
    os.chdir(mxdir)
    with open('mvlist','r') as f: mvlist = f.readlines()
    mvprocs = []
    args = ['combineTool.py','-M','CollectLimits']
    for mv in mvlist:
        mv = mv.replace('\n','')
        args.append( 'higgsCombineMx%s_Mv%s.AsymptoticLimits.mH%s.root' % (mx,mv,mv) )
    args += ['-o','zprimeMx%s_Mv%s.json']
    if show:
        mxproc = cPopen(args)
        proc.wait()
    else:
        mxproc = cPopen(args,stdout=PIPE,stderr=STDOUT)
    os.chdir(cwd)
    return { mx:mxproc }
##############################################################################
def runMxdir(mxdir,show=False):
    mx = mxdir.replace('Mx_','').replace('/','')
    cwd = os.getcwd()
    os.chdir(mxdir)
    with open('mvlist','r') as f: mvlist = f.readlines()
    mvprocs = {}
    for mv in mvlist:
        mv = mv.replace('\n','')
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
if __name__ == "__main__":
    parser = OptionParser()
    parser.add_option("-d","--dir",help='Specify the directory to run limits in',action='store',type='str',default=None)
    parser.add_option("-v","--verbose",help='Show output from combine',action='store_true',default=False)
    options,args = parser.parse_args()
    if options.dir == None:
        print "Please specify a director to run limits in."
        exit()
    os.chdir(options.dir)
    mxdirs = [ dir for dir in os.listdir('.') if re.search(r'Mx_\d+$',dir) ]
    procs = {}
    print 'Running Limits'
    for mxdir in sorted(mxdirs): procs.update( runMxdir(mxdir,show=options.verbose) )
    printProcs(procs,'Mx Limits')
    print 'Collecting Limits'
    for mxdir in sorted(mxdirs): procs.update( collectMxdir(mxdir,show=options.verbose) )
    printProcs(procs,'Mx Output')
#################################################################################################
