#!/usr/bin/env python
from argparse import ArgumentParser
import os
import sys
sys.path.append('PlotTool')
from PlotTool import SysInfo
from subprocess import Popen,STDOUT,PIPE
import re
from shutil import copyfile

cmssw_base = os.getenv("CMSSW_BASE")
outdir_base = "/afs/hep.wisc.edu/home/ekoenig4/public_html/MonoJet/Plots%s/ExpectedLimits/"
ch_order = ('sr','we','wm','ze','zm','ga')

def channel_order(ch1,ch2):
    for i,ch in enumerate(ch_order):
        if ch in ch1: i1 = i
        if ch in ch2: i2 = i
    if i1 < i2: return -1
    elif i1 == i2:
            y1 = re.findall('\d\d\d\d',ch1)
            y2 = re.findall('\d\d\d\d',ch2)
            if any(y1) and any(y2):
                y1 = int(y1[0]); y2 = int(y2[0])
                if y1 < y2: return -1
    return 1
def getargs():
    parser = ArgumentParser()
    parser.add_argument("-d","--dir",help="specify directory to run pulls in",nargs='+',action="store",type=str,required=True)
    parser.add_argument("-s","--signal",help="specify signal sample to run pulls on",action="store",type=str,default="Mchi1_Mphi1000")
    return parser.parse_args()
def mvpulls(info):
    outdir = outdir_base % info.year
    outname = 'pulls_%s.pdf' % info.sysdir
    output = '%s/%s/%s/%s' % (outdir,info.variable,info.sysdir,outname)
    if not os.path.isfile('pulls/pulls.pdf'): return
    print 'Moving pulls/pulls.pdf to %s' % output
    copyfile('pulls/pulls.pdf',output)
def export():
    from ROOT import TFile
    TFile.Open("test.root").Get("nuisances").Print("pulls.pdf")
def run(command):
    print command
    Popen(command.split()).wait()
def runPulls(path,args):
    print path
    if 'nSYS' in path and 'nSTAT' in path: return
    info = SysInfo(path)
    home = os.getcwd()
    os.chdir(path)
    cwd = os.getcwd()
    sysdir = next( sub for sub in cwd.split('/') if '.sys' in sub )
    if not os.path.isdir("pulls"): os.mkdir("pulls")
    os.chdir("pulls")
    workspace = "%s_sr.root" % args.signal
    mx = args.signal.split("_")[0].replace("Mchi","")
    mv = args.signal.split("_")[1].replace("Mphi","")


    #--- Combine Cards and Mask SR ---#
    channels = [ card.replace('datacard_','') for card in os.listdir('../') if 'datacard' in card ]
    channels.sort(channel_order)
    sr_channel = [ channel for channel in channels if 'sr' in channel ]
    combine_cards = ['combineCards.py'] + ['%s=../datacard_%s' % (channel,channel) for channel in channels] + ['>','datacard']
    text2workspace = ['text2workspace.py','datacard','--channel-masks','-m',mv,'-o',workspace]
    sr_mask = [','.join(['mask_%s=1' % channel for channel in sr_channel])]
    
    combine = ("combine -M FitDiagnostics -d %s -t -1 " % workspace) + ' '.join(sr_mask)
    diffNuisances = "python %s/src/HiggsAnalysis/CombinedLimit/test/diffNuisances.py fitDiagnostics.root -g test.root --abs" % cmssw_base
    
    with open('run_pulls.sh','w') as f:
        f.write('set -o xtrace\n')
        f.write('\n'.join([combine_cards,text2workspace,combine,diffNuisances]))
    run("sh run_pulls.sh")
    export()
    os.chdir(cwd)
    mvpulls(info)
    os.chdir(home)
if __name__ == "__main__":
    args = getargs()
    for path in args.dir: runPulls(path,args)
