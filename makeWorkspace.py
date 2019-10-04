#!/usr/bin/env python
from ROOT import *
import os
from shutil import rmtree
from argparse import ArgumentParser
from array import array
from fitting.createWorkspace import createWorkspace
from fitting.createDatacards import createDatacards
import re
from subprocess import Popen,PIPE,STDOUT

mv_exclude = ['10000']
mx_exclude = ['1']
mx_include = ['10','50','100']

def GetMxlist(sysfile):
    rfile = TFile.Open(sysfile)
    rfile.cd('sr')
    regexp = re.compile(r'Mx\d+_Mv\d+$')
    mxlist = {}
    for sample in gDirectory.GetListOfKeys():
        if regexp.search(sample.GetName()):
            mx = sample.GetName().split('_')[0].replace('Mx','')
            if mx not in mx_include: continue
            mv = sample.GetName().split('_')[1].replace('Mv','')
            if mx not in mxlist: mxlist[mx] = []
            if mv in mv_exclude: continue
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
    card = card.replace('Mx10_Mv1000','Mx%s_Mv$MASS' % mx)
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
    try: args = parser.parse_args()
    except ValueError as err:
        print err
        parser.print_help()
        exit()
    return args
#####
def makeWorkspace():
    if not os.path.isdir("Limits/"): os.mkdir("Limits/")

    args = getargs()
    mxlist = GetMxlist(args.input)
    fname = args.input.split('/')[-1]
    sysfile = os.path.abspath(args.input)
    ##########################################################
    dir = 'Limits/'+fname.replace('.root', '')
    dir = os.path.abspath(dir)
    
    if args.reset and os.path.isdir(dir): rmtree(dir)
    if not os.path.isdir(dir): os.mkdir(dir)
    ##################################################
    os.chdir(dir)
    wsfname = 'workspace.root'
    if not os.path.isfile(wsfname): createWorkspace(sysfile)
    createDatacards(wsfname)
    ########################################################
    for mx,mvlist in mxlist.items(): makeMxDir(mx,mvlist,cr=args.cr)
######################################################################
if __name__ == "__main__": makeWorkspace()
    
