#!/usr/bin/env python
from argparse import ArgumentParser
import os
from subprocess import Popen,STDOUT,PIPE
import re
from shutil import copyfile

cmssw_base = os.getenv("CMSSW_BASE")
outdir_base = "/afs/hep.wisc.edu/home/ekoenig4/public_html/MonoZprimeJet/Plots%s/ExpectedLimits/"

text2workspace = "text2workspace.py ../Mx_%s/datacard -m %s -o %s"
combine = "combine -M FitDiagnostics -d %s -t -1"
diffNuisances = "python %s/src/HiggsAnalysis/CombinedLimit/test/diffNuisances.py fitDiagnostics.root -g test.root --abs --all" % cmssw_base

def getargs():
    parser = ArgumentParser()
    parser.add_argument("-d","--dir",help="specify directory to run pulls in",nargs='+',action="store",type=str,required=True)
    parser.add_argument("-s","--signal",help="specify signal sample to run pulls on",action="store",type=str,default="Mx1_Mv1000")
    return parser.parse_args()
def mvpulls(sysdir):
    first = sysdir.split('_')[0]
    second = sysdir.split('_')[1]
    variable = re.findall('^.*[\+-]',first)
    if not any(variable): variable = first
    else: variable = variable[0][:-1]
    year = re.findall('\d\d\d\d',second)[0]
    outdir = outdir_base % year
    outname = 'pulls_%s.pdf' % sysdir.replace('.sys','')
    output = '%s/%s/%s' % (outdir,variable,outname)
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
    home = os.getcwd()
    os.chdir(path)
    cwd = os.getcwd()
    sysdir = next( sub for sub in cwd.split('/') if '.sys' in sub )
    if not os.path.isdir("pulls"): os.mkdir("pulls")
    os.chdir("pulls")
    workspace = "%s_sr.root" % args.signal
    mx = args.signal.split("_")[0].replace("Mx","")
    mv = args.signal.split("_")[1].replace("Mv","")

    run( text2workspace % (mx,mv,workspace) )
    run( combine % workspace )
    run( diffNuisances )
    export()
    os.chdir(cwd)
    mvpulls(sysdir)
    os.chdir(home)
if __name__ == "__main__":
    args = getargs()
    for path in args.dir: runPulls(path,args)
