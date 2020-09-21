#!/usr/bin/env python
from ROOT import *
import os
import sys
from shutil import rmtree,copyfile
from argparse import ArgumentParser
from array import array
from fitting import *
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
def makeMphiDir(mv,options,procmap=None):
    if mv == '10000': return
    cwd = os.getcwd()
    mvdir = 'Mphi_%s' % mv
    print '--Create %s Directory' % mvdir
    if not os.path.isdir(mvdir): os.mkdir(mvdir)
    os.chdir(mvdir)
    text2workspace = ['text2workspace.py','datacard','-m',mv,'-o','%s/workspace_Mphi%s.root' % (mvdir,mv)]
    with open('make_workspace.sh','w') as f:
        f.write('#!/bin/sh\n')
        f.write('cd ../\n')
        f.write(' '.join(text2workspace)+'\n')
    proc = Popen(['sh','make_workspace.sh'],stdout=PIPE,stderr=STDOUT);
    if procmap is not None: procmap[os.getcwd()] = proc
    else:                   proc.wait()
    os.chdir(cwd)
def makeMchiDir(mx,mvlist,yearlist,options,procmap=None):
    cwd = os.getcwd()
    regions = []
    for ch in ('sr','we','wm','ze','zm','ga'):
        for year in yearlist:
            if year == "2016" and ch == "ga": continue
            regions.append('%s_%s' % (ch,year))
    mxdir = 'Mchi_%s' % mx
    print 'Creating %s Directory' % mxdir
    if not os.path.isdir(mxdir): os.mkdir(mxdir)
    os.chdir(mxdir)
    combine_cards = ['combineCards.py']
    for region in regions: combine_cards.append('%s=../datacard_%s' % (region,region))
    combine_cards += ['>','datacard']
    replace_mx = ['sed','-i',"'s/Mchi1/Mchi%s/g'" % mx,'datacard']
    replace_mv = ['sed','-i',"'s/Mphi100/Mphi$MASS/g'",'datacard']
    with open('make_datacard.sh','w') as f:
        f.write('#!/bin/sh\n')
        f.write(' '.join(combine_cards)+'\n')
        f.write(' '.join(replace_mx)+'\n')
        f.write(' '.join(replace_mv)+'\n')
    proc = Popen(['sh','make_datacard.sh'],stdout=PIPE,stderr=STDOUT); proc.wait()
    procmap = {}
    for mv in mvlist: makeMphiDir(mv,options,procmap)
    printProcs(procmap,"Mphi Directories")
    os.chdir(cwd)
#####
def getargs():    
    # parser = ArgumentParser(description='Make workspace for generating limits based on input systematics file')
    parser.add_argument("-i","--input",help="Specify input systematics file to generate limits from",default=None,required=True)
    parser.add_argument("-o","--output",help="Specify output directory")
    parser.add_argument('-r','--reset',help="Remove directory before creating workspace if it is already there",action='store_true',default=False)
    parser.add_argument('--combined',help='Create combined limit cards',action='store_true',default=False)
    try: args = parser.parse_args()
    except ValueError as err:
        print err
        parser.print_help()
        exit()
    return args
#####
def yearWorkspace(syscat,args):
    isScaled = os.path.isfile('signal_scaling.json')
    if not args.output:
        sysdir = 'Limits/%s' % syscat.var.GetTitle()
    else: sysdir = "Limits/%s" % args.output
    outfname = '%s/workspace_%s.root' % (sysdir,syscat.year)
    if isScaled: copyfile('signal_scaling.json','%s/signal_scaling.json' % sysdir)
    if not os.path.isfile(outfname) or args.reset:
        return createWorkspace(syscat,outfname=outfname,isScaled=isScaled)
####################
def makeWorkspace(syscat,args):
    print "Making Workspace for",syscat.GetName()
    cwd = os.getcwd()
    if not args.output:
        sysdir = 'Limits/%s' % syscat.var.GetTitle()
    else: sysdir = "Limits/%s" % args.output
    if not os.path.isdir(sysdir): os.mkdir(sysdir)
    ws = yearWorkspace(syscat,args)
    syscat.ws = ws
    sysdir = '%s/%s' % (sysdir,syscat.GetName().split('/')[-1].replace(".root",""))
    syscat.sysdir = sysdir
    if not os.path.isdir(sysdir): os.mkdir(sysdir)
    os.chdir(sysdir)
    createDatacards('../workspace_%s.root' % syscat.year,syscat.year)
    # for mx,mvlist in syscat.getSignalList().items(): makeMchiDir(mx,mvlist,[syscat.year],args)
    os.chdir(cwd)
    return syscat
####################
def combineWorkspace(syscats,args):
    print "Making Combined Workspace"
    cwd = os.getcwd()
    sysdir = syscats[0].sysdir.replace("%s.sys"%syscats[0].year,"Run2.sys")
    if not os.path.isdir(sysdir): os.mkdir(sysdir)
    for datacard in os.listdir("."):
        if "datacard" in datacard: os.remove(datacard)
    for syscat in syscats:
        for datacard in os.listdir(syscat.sysdir):
            if "datacard" in datacard:
                print "Copying %s/%s" %(syscat.sysdir,datacard)
                copyfile("%s/%s"%(syscat.sysdir,datacard),"%s/%s"%(sysdir,datacard))
    os.chdir(sysdir)
    signalist = syscat.getSignalList()
    for mx,mvlist in signalist.items(): makeMchiDir(mx,mvlist,[ syscat.year for syscat in syscats ],args)
    os.chdir(cwd)
####################
def main():
    if not os.path.isdir('Limits/'): os.mkdir('Limits/')
    args = getargs()

    sysfile = SysFile(args.input)
    for category in sysfile.categories.values(): makeWorkspace(category,args)
    if args.combined:
        combineWorkspace(sysfile.categories.values(),args)
    return sysfile
####################
if __name__ == "__main__": a=main()
    
