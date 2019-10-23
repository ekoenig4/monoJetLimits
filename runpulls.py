#!/usr/bin/env python
from argparse import ArgumentParser
import os
from subprocess import Popen,STDOUT,PIPE

cmssw_base = os.getenv("CMSSW_BASE")

text2workspace = "text2workspace.py ../Mx_%s/datacard -m %s -o %s"
combine = "combine -M FitDiagnostics -d %s -t -1"
diffNuisances = "python %s/src/HiggsAnalysis/CombinedLimit/test/diffNuisances.py fitDiagnostics.root -g test.root --abs --all" % cmssw_base

def getargs():
    parser = ArgumentParser()
    parser.add_argument("-d","--dir",help="specify directory to run pulls in",action="store",type=str,required=True)
    parser.add_argument("-s","--signal",help="specify signal sample to run pulls on",action="store",type=str,default="Mx1_Mv1000")
    return parser.parse_args()
def export():
    from ROOT import TFile
    TFile.Open("test.root").Get("nuisances").Print("test.pdf")
def run(command):
    print command
    Popen(command.split()).wait()

if __name__ == "__main__":
    args = getargs()
    os.chdir(args.dir)
    if not os.path.isdir("test"): os.mkdir("test")
    os.chdir("test")
    workspace = "%s_sr.root" % args.signal
    mx = args.signal.split("_")[0].replace("Mx","")
    mv = args.signal.split("_")[1].replace("Mv","")

    run( text2workspace % (mx,mv,workspace) )
    run( combine % workspace )
    run( diffNuisances )
    export()
