#!/usr/bin/env python
from ROOT import *
import os
import sys
from shutil import rmtree
from argparse import ArgumentParser
from array import array
from fitting.createWorkspace import createWorkspace
from fitting.createDatacards import createDatacards,signal
import re
from subprocess import Popen,PIPE,STDOUT

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
def GetMxlist(sysfile):
    rfile = TFile.Open(sysfile)
    rfile.cd('sr')
    regexp = re.compile(r'Mx\d+_Mv\d+$')
    mxlist = {}
    def valid_signal(hs):
        # some signal has negative events, ignore them
        for ibin in range(1,len(hs)):
            if hs[ibin] < 0: return False
        return True
    for sample in gDirectory.GetListOfKeys():
        if regexp.search(sample.GetName()):
            if not valid_signal(gDirectory.Get(sample.GetName())): continue
            mx = sample.GetName().split('_')[0].replace('Mx','')
            mv = sample.GetName().split('_')[1].replace('Mv','')
            if mx not in mxlist: mxlist[mx] = []
            mxlist[mx].append(mv)
    return mxlist
def makeMvDir(mv,options,procmap=None):
    cwd = os.getcwd()
    mvdir = 'Mv_%s' % mv
    print '--Create %s Directory' % mvdir
    if not os.path.isdir(mvdir): os.mkdir(mvdir)
    os.chdir(mvdir)
    text2workspace = ['text2workspace.py','datacard','-m',mv,'-o','%s/workspace_Mv%s.root' % (mvdir,mv)]
    with open('make_workspace.sh','w') as f:
        f.write('#!/bin/sh\n')
        f.write('cd ../\n')
        f.write(' '.join(text2workspace)+'\n')
    proc = Popen(['sh','make_workspace.sh']);
    if procmap is not None: procmap[os.getcwd()] = proc
    else:                   proc.wait()
    os.chdir(cwd)
def makeMxDir(mx,mvlist,options,procmap=None):
    cwd = os.getcwd()
    if options.cr: regions = ('sr','e','m','ee','mm')
    else:  regions = ('sr',)
    mxdir = 'Mx_%s' % mx
    print 'Creating %s Directory' % mxdir
    if not os.path.isdir(mxdir): os.mkdir(mxdir)
    os.chdir(mxdir)
    combine_cards = ['combineCards.py']
    for region in regions: combine_cards.append('%s=../datacard_%s' % (region,region))
    combine_cards += ['>','datacard']
    replace_mx = ['sed','-i',"'s/Mx1/Mx%s/g'" % mx,'datacard']
    replace_mv = ['sed','-i',"'s/Mv1000/Mv$MASS/g'",'datacard']
    with open('make_datacard.sh','w') as f:
        f.write('#!/bin/sh\n')
        f.write(' '.join(combine_cards)+'\n')
        f.write(' '.join(replace_mx)+'\n')
        f.write(' '.join(replace_mv)+'\n')
    proc = Popen(['sh','make_datacard.sh']); proc.wait()
    procmap = {}
    for mv in mvlist: makeMvDir(mv,options,procmap)
    printProcs(procmap,mxdir)
    os.chdir(cwd)
#####
def getargs():
    def sysfile(arg):
        tfile = TFile.Open(arg)
        valid = True
        if tfile.IsZombie(): raise ValueError()
        validdir = ['sr','e','ee','m','mm']
        for dir in validdir:
            if tfile.GetDirectory(dir) != None: return arg
        raise ValueError()
    
    parser = ArgumentParser(description='Make workspace for generating limits based on input systematics file')
    parser.add_argument("-i","--input",help="Specify input systematics file to generate limits from",action="store",type=sysfile,default=None,required=True)
    parser.add_argument('--cr',help="Include CR datacards in datacard",action='store_true',default=False)
    parser.add_argument('-r','--reset',help="Remove directory before creating workspace if it is already there",action='store_true',default=False)
    parser.add_argument('--no-sys',help="Remove systematics from datacards",action='store_true',default=False)
    parser.add_argument('--no-stat',help="Remove statistical uncertainty from datacards",action='store_true',default=False)
    try: args = parser.parse_args()
    except ValueError as err:
        print err
        parser.print_help()
        exit()
    return args
#####
def modify(dir,args):
    if args.no_sys: return dir.replace('.sys','nSy.sys')
    elif args.cr and args.no_stat: return dir.replace('.sys','ntC.sys')
    elif args.cr:     return dir.replace('.sys','wCR.sys')
    elif args.no_stat:return dir.replace('.sys','nSt.sys')
    return dir
#####
def makeWorkspace():
    if not os.path.isdir("Limits/"): os.mkdir("Limits/")

    args = getargs()
    year = re.findall(r"20\d\d",args.input)[0]
    if not os.path.isdir("Limits/%s/" % year): os.mkdir("Limits/%s/" % year)
    
    mxlist = GetMxlist(args.input)
    fname = args.input.split('/')[-1]
    sysfile = os.path.abspath(args.input)
    ##########################################################
    dir = ('Limits/%s/' % year) +fname.replace('.root', '')
    dir = modify(dir,args)
    dir = os.path.abspath(dir)
    
    if args.reset and os.path.isdir(dir): rmtree(dir)
    if not os.path.isdir(dir): os.mkdir(dir)
    ##################################################
    os.chdir(dir)
    wsfname = 'workspace.root'
    if not os.path.isfile(wsfname): createWorkspace(sysfile,options=args)
    createDatacards(wsfname,options=args)
    ########################################################
    for mx,mvlist in mxlist.items(): makeMxDir(mx,mvlist,options=args)
######################################################################
if __name__ == "__main__": makeWorkspace()
    
