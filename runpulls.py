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
    parser.add_argument("-g",help="specify output root file name",type=str,default="diffNuisances_result.root")

    known,unknown = parser.parse_known_args()

    known.diff = unknown
    return known
def mvpulls(info):
    outdir = outdir_base % info.year
    outname = 'pulls_%s.pdf' % info.sysdir
    output = '%s/%s/%s/%s' % (outdir,info.variable,info.sysdir,outname)
    if not os.path.isfile('pulls/pulls.pdf'): return
    print 'Moving pulls/pulls.pdf to %s' % output
    copyfile('pulls/pulls.pdf',output)
def export(info,args,npull=15):
    from ROOT import TFile,gROOT,gStyle,TPad,TCanvas
    from math import ceil
    gROOT.SetStyle("Plain")
    gStyle.SetOptFit(1)
    gStyle.SetOptStat(0)
    gROOT.SetBatch(1)
    
    outdir = outdir_base % info.year
    outvar = '%s/%s/' % (outdir,info.variable)
    if not os.path.isdir(outvar): os.mkdir(outvar)
    outsys = '%s/%s' % (outvar,info.sysdir)
    if not os.path.isdir(outsys): os.mkdir(outsys)
    
    outname = 'pulls_%s.pdf' % info.variable
    output = '%s/%s' % (outsys,outname)
    pulls = TFile.Open(args.g)
    canvas = pulls.Get("nuisances")
    objlist = canvas.GetListOfPrimitives()
    prefit = objlist.At(0).Clone()
    fit_bg = objlist.At(2).Clone()
    fit_bs = objlist.At(3).Clone()
    legend = objlist.At(6).Clone()

    prefit.GetYaxis().SetRangeUser(-4,4)

    legend.SetX1(0.76)
    legend.SetX2(0.99)

    npages = int(ceil(float(prefit.GetNbinsX())/npull))
    for page in range(npages):
        canvas = TCanvas()
        canvas.SetBottomMargin(0.15)
        canvas.SetRightMargin(0.25)
        canvas.SetGridx()
        canvas.Draw()
        xlo = page * npull + 1
        xhi = page * npull + npull
        if xhi > prefit.GetNbinsX(): xhi = prefit.GetNbinsX()
        prefit.GetXaxis().SetRange(xlo,xhi)

        prefit.Draw("E2")
        prefit.Draw("histsame")
        fit_bg.Draw("EPsame")
        fit_bs.Draw("EPsame")
        legend.Draw()

        if page == 0: canvas.SaveAs(output+"(")
        elif page+1 == npages: canvas.SaveAs(output+")")
        else: canvas.SaveAs(output)
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
    if not os.path.isdir("cr_fit"):
        print "Please first run:\n\t ./runCRfit.py -d %s" % path
        os.chdir(home)
        return

    os.chdir('cr_fit')
    #--- Combine Cards and Mask SR ---#
    diffNuisances = ["python","%s/src/HiggsAnalysis/CombinedLimit/test/diffNuisances.py"%os.getenv("CMSSW_BASE"),"fitDiagnostics_fit_CRonly_result.root","-g",args.g]
    diffNuisances += args.diff
    
    with open('run_pulls.sh','w') as f:
        f.write('set -o xtrace\n')
        f.write(' '.join(diffNuisances)+'\n')
    run("sh run_pulls.sh")
    export(info,args)
    os.chdir(cwd)
    mvpulls(info)
    os.chdir(home)
if __name__ == "__main__":
    args = getargs()
    for path in args.dir: runPulls(path,args)
