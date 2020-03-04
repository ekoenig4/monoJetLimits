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
outdir_base = "/afs/hep.wisc.edu/home/ekoenig4/public_html/MonoZprimeJet/Plots%s/ExpectedLimits/"

text2workspace = "text2workspace.py ../Mchi_%s/datacard -m %s -o %s"
combine = "combine -M FitDiagnostics -d %s -t -1"
diffNuisances = "python %s/src/HiggsAnalysis/CombinedLimit/test/diffNuisances.py fitDiagnostics.root -g test.root --abs --all" % cmssw_base

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

    run( text2workspace % (mx,mv,workspace) )
    run( combine % workspace )
    run( diffNuisances )
    export()
    os.chdir(cwd)
    mvpulls(info)
    os.chdir(home)
if __name__ == "__main__":
    args = getargs()
    for path in args.dir: runPulls(path,args)
