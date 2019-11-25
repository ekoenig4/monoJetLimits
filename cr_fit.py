#!/usr/bin/env python
import os
from shutil import copyfile
import sys
from argparse import ArgumentParser
from subprocess import Popen,PIPE,STDOUT
from time import time
import json
import re
from ROOT import *

gROOT.SetBatch(1)

outdir_base = "/afs/hep.wisc.edu/home/ekoenig4/public_html/MonoZprimeJet/Plots%s/ExpectedLimits/"

mclist = ['ZJets','WJets','DYJets','GJets','TTJets','QCD','EWK']

crmap = {
    'e':{'mc':'WJets','leg':'W #rightarrow e#nu'},
    'm':{'mc':'WJets','leg':'W #rightarrow #mu#nu'},
    'ee':{'mc':'DYJets','leg':'Z #rightarrow ee'},
    'mm':{'mc':'DYJets','leg':'Z #rightarrow #mu#mu'}
}
def getLegend(xmin=0.5,ymin=0.65,xmax=0.7,ymax=0.887173):
    leg = TLegend(xmin,ymin,xmax,ymax,"")
    leg.SetFillColor(kWhite);
    leg.SetFillStyle(0);
    leg.SetTextSize(0.025);
    return leg
def getCMSText(year):
    x1,y1 = 0.62,0.907173
    texS = TLatex(x1,y1,("XX fb^{-1} (13 TeV, %s)" % year));#VS
    texS.SetNDC();
    texS.SetTextFont(42);
    texS.SetTextSize(0.040);
    texS.Draw();

    x2,y2 = 0.15,0.837173
    texS1 = TLatex(x2,y2,"#bf{CMS} #it{Preliminary}"); 
    texS1.SetNDC();
    texS1.SetTextFont(42);
    texS1.SetTextSize(0.040);
    texS1.Draw();
    return texS,texS1
def data_style(graph):
    graph.SetTitle("")
    graph.SetMarkerStyle(20)
def fit_style(hs,color):
    hs.SetTitle("")
    hs.GetYaxis().SetTitle("Events")
    hs.SetLineColor(color)
    hs.SetLineWidth(2)
    hs.SetFillStyle(0)
    hs.SetFillColor(0)
def set_bounds(hs):
    ymin = min( hs[ibin] for ibin in range(1,hs.GetNbinsX()+1) if hs[ibin] != 0)
    ymax = max( hs[ibin] for ibin in range(1,hs.GetNbinsX()+1) if hs[ibin] != 0)

    hs.SetMinimum(0.05)
    hs.SetMaximum(ymax*(10**2.5))
def ratio_style(ratio,color,rymin=0.65,rymax=1.35):
    gPad.SetGridy();
    ratio.SetMarkerStyle(20)
    ratio.SetMarkerColor(color)
    ratio.SetTitle("")
    ratio.GetYaxis().SetRangeUser(rymin,rymax);
    ratio.SetStats(0);
    ratio.GetYaxis().CenterTitle();
    ratio.GetYaxis().SetTitle("Data/MC")
    ratio.SetMarkerStyle(20);
    ratio.SetMarkerSize(1);
    ratio.GetYaxis().SetLabelSize(0.1);
    ratio.GetYaxis().SetTitleSize(0.1);
    ratio.GetYaxis().SetLabelFont(42);
    ratio.GetYaxis().SetTitleFont(42);
    ratio.GetYaxis().SetTitleOffset(0.35);
    ratio.GetYaxis().SetNdivisions(4);
    ratio.GetYaxis().SetTickLength(0.05);
    
    ratio.GetXaxis().SetLabelSize(0.1);
    ratio.GetXaxis().SetTitleSize(0.1);
    ratio.GetXaxis().SetLabelFont(42);
    ratio.GetXaxis().SetTitleFont(42);
    ratio.GetXaxis().SetTitleOffset(1.2);
    ratio.GetXaxis().SetTickLength(0.05);
def makeHistogram(graph,template):
    hs = template.Clone();
    npoints = graph.GetN()
    for i in range(npoints):
        x,y=Double(0),Double(0)
        graph.GetPoint(i,x,y)
        xerr = graph.GetErrorX(i)
        yerr = graph.GetErrorY(i)
        hs.SetBinContent(i+1,y)
        hs.SetBinError(i+1,yerr)
    return hs;
def getOtherBkg(cr,tfile):
    bkg = None
    tdir = tfile.Get('shapes_prefit/%s' % cr)
    for mc in mclist:
        if crmap[cr]['mc'] in mc: continue
        tmp = tdir.Get('%s' % mc)
        if tmp == None: continue
        if bkg is None: bkg = tmp
        else:           bkg.Add(tmp)
    bkg.SetFillColor(kGray)
    bkg.SetLineColor(kBlack)
    return bkg
def plotCR(cr,tfile,info):
    prefit_hs = tfile.Get('shapes_prefit/%s/total_background' % (cr))
    postfit_hs = tfile.Get('shapes_fit_b/%s/total_background' % (cr))
    data_graph = tfile.Get('shapes_prefit/%s/data' % cr)

    other_bkg = getOtherBkg(cr,tfile)

    c = TCanvas("c", "canvas",800,800);
    gStyle.SetOptStat(0);
    gStyle.SetLegendBorderSize(0);
    #c.SetLeftMargin(0.15);
    #c.SetLogy();
    #c.cd();
    
    pad1 = TPad("pad1","pad1",0.01,0.25,0.99,0.99);
    pad1.Draw(); pad1.cd();
    pad1.SetLogy();
    pad1.SetFillColor(0); pad1.SetFrameBorderMode(0); pad1.SetBorderMode(0);
    pad1.SetBottomMargin(0.);

    prefit_hs.Draw("hist"); fit_style(prefit_hs,kRed); set_bounds(prefit_hs)
    postfit_hs.Draw("hist same"); fit_style(postfit_hs,kBlue)
    other_bkg.Draw("hist same")
    data_graph.Draw("pex0 same"); data_style(data_graph)

    leg = getLegend()
    leg.AddEntry(data_graph,"Data","lp")
    leg.AddEntry(postfit_hs,"Post-fit (%s)" % crmap[cr]['leg'],'l')
    leg.AddEntry(prefit_hs,"Pre-fit (%s)" % crmap[cr]['leg'],'l')
    leg.AddEntry(other_bkg,"Other Backgrounds",'f')
    leg.Draw()

    texCMS,texLumi = getCMSText(info.year)

    ##############################
    c.cd();
    pad2 = TPad("pad2","pad2",0.01,0.01,0.99,0.25);
    pad2.Draw(); pad2.cd();
    pad2.SetFillColor(0); pad2.SetFrameBorderMode(0); pad2.SetBorderMode(0);
    pad2.SetTopMargin(0);
    pad2.SetBottomMargin(0.35);

    prefit_ratio = makeHistogram(data_graph,prefit_hs); prefit_ratio.Divide(prefit_hs)
    postfit_ratio = makeHistogram(data_graph,postfit_hs); postfit_ratio.Divide(postfit_hs)

    prefit_ratio.Draw('pex0'); ratio_style(prefit_ratio,kRed)
    postfit_ratio.Draw('pex0same'); ratio_style(postfit_ratio,kBlue)

    outname = 'fit_CRonly_%s_%s.png' % (cr,info.sysdir.replace('.sys',''))
    output = '%s/%s/%s' % (info.outdir,info.variable,outname)
    c.SaveAs(output)
def plotCRFit(path,info):
    tfile = TFile.Open("fitDiagnostics_fit_CRonly_result.root")
    for cr in crmap    : plotCR(cr,tfile,info)
##############################################################################
def runFit(args):
    if os.path.isfile('fitDiagnostics_fit_CRonly_result.root') and not args.reset: return
    combine_cards = ['combineCards.py','sr=../datacard_sr']
    for cr in crmap: combine_cards.append('%s=../datacard_%s' % (cr,cr))
    combine_cards += ['>','datacard']
    text2workspace = ['text2workspace.py','datacard','--channel-masks']
    with open('make_workspace.sh','w') as f:
        f.write("#!/bin/sh\n")
        f.write(' '.join(combine_cards)+'\n')
        f.write(' '.join(text2workspace)+'\n')
    proc = Popen(['sh','make_workspace.sh']); proc.wait()
##############################################################################
def parseInfo(path):
    sysdir = next( sub for sub in path.split('/') if '.sys' in sub )
    class Info: pass
    info = Info()
    info.sysdir = sysdir
    first = sysdir.split('_')[0]
    second = sysdir.split('_')[1]
    info.variable = re.findall('^.*[\+-]',first)
    if not any(info.variable): info.variable = first
    else: info.variable = info.variable[0][:-1]
    info.year = re.findall('\d\d\d\d',second)[0]
    info.outdir = outdir_base % info.year
    return info
##############################################################################
def runDirectory(path,args):
    print path
    info = parseInfo(path)
    cwd = os.getcwd()
    os.chdir(path)
    if not os.path.isdir('cr_fit'): os.mkdir('cr_fit')
    os.chdir('cr_fit')
    runFit(args)
    plotCRFit(path,info)
##############################################################################
def getargs():
    def directory(arg):
        if os.path.isdir(arg): return arg
        raise ValueError()
    def signal(arg):
        regex = re.compile(r"Mx\d*_Mv\d*$")
        if regex.match(arg): return arg
        raise ValueError()
    parser = ArgumentParser(description='Run all avaiable limits in specified directory')
    parser.add_argument("-d","--dir",help='Specify the directory to run limits in',nargs='+',action='store',type=directory,required=True)
    parser.add_argument("-r","--reset",help='Rerun combine fit diagnositics',action='store_true',default=False)
    try: args = parser.parse_args()
    except:
        parser.print_help()
        exit()
    return args
##############################################################################
if __name__ == "__main__":
    args = getargs()
    for path in args.dir: runDirectory(path,args)
##############################################################################
