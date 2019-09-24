#!/usr/bin/env python
from ROOT import *
import os
from optparse import OptionParser
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
def makeWorkspace():
    if not os.path.isdir("Limits/"): os.mkdir("Limits/")
    
    parser = OptionParser()
    parser.add_option("-i","--input",help="Specify input systematics file to generate limits from",action="store",type="str",default=None)
    parser.add_option('--cr',help="Include CR datacards in datacard",action='store_true',default=False)
    options,args = parser.parse_args()

    
    mxlist = GetMxlist(options.input)
    fname = options.input.split('/')[-1]
    sysfile = os.path.abspath(options.input)
    ##########################################################
    dir = 'Limits/'+fname.replace('.root', '')
    if options.cr: dir = dir.replace('.sys','wCR.sys')
    dir = os.path.abspath(dir)
    if not os.path.isdir(dir): os.mkdir(dir)
    ##################################################
    os.chdir(dir)
    wsfname = 'workspace.root'
    if not os.path.isfile(wsfname): createWorkspace(sysfile)
    createDatacards(wsfname)
    ########################################################
    for mx,mvlist in mxlist.items(): makeMxDir(mx,mvlist,cr=options.cr)
######################################################################
if __name__ == "__main__": makeWorkspace()
    
