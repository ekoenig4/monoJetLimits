#!/usr/bin/env python
from ROOT import *
import os
from shutil import rmtree
from argparse import ArgumentParser
from array import array
from fitting.createWorkspace import createWorkspace
from fitting.createDatacards import createDatacards,signal
import re
from subprocess import Popen,PIPE,STDOUT

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
def makeMxDir(mx,mvlist,cr=False):
    cwd = os.getcwd()
    if cr: regions = ('sr','e','m','ee','mm')
    else:  regions = ('sr',)
    mxdir = 'Mx_%s' % mx
    print 'Creating %s Directory' % mxdir
    if not os.path.isdir(mxdir): os.mkdir(mxdir)
    os.chdir(mxdir)
    args = ['combineCards.py']
    for region in regions: args.append('%s=../datacard_%s' % (region,region))
    args += ['>','datacard']
    command = ''
    for arg in args: command += '%s ' % arg 
    os.system( command )

    with open('datacard','r') as f: card = f.read()
    card = card.replace(signal,'Mx%s_Mv$MASS' % mx)
    with open('datacard','w') as f: f.write(card)
    with open('mvlist','w') as f:
        for mv in mvlist:
            f.write(mv+'\n')
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
    try: args = parser.parse_args()
    except ValueError as err:
        print err
        parser.print_help()
        exit()
    return args
#####
def modify(dir,args):
    if args.no_sys: return dir.replace('.sys','nSy.sys')
    if args.cr:     return dir.replace('.sys','wCR.sys')
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
    if not os.path.isfile(wsfname): createWorkspace(sysfile,doCR=args.cr)
    createDatacards(wsfname,doCR=args.cr,noSys=args.no_sys)
    ########################################################
    for mx,mvlist in mxlist.items(): makeMxDir(mx,mvlist,cr=args.cr)
######################################################################
if __name__ == "__main__": makeWorkspace()
    
