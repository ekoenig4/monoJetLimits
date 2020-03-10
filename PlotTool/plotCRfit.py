import os
from shutil import copyfile
import sys
from argparse import ArgumentParser
from subprocess import Popen,PIPE,STDOUT
from time import time
import json
import re
from ROOT import *
from PlotTool import *

gROOT.SetBatch(1)

outdir_base = "/afs/hep.wisc.edu/home/ekoenig4/public_html/MonoJet/Plots%s/ExpectedLimits/"

mclist = ['ZJets','WJets','DYJets','GJets','TTJets','QCD','EWK']

prefit_color = kOrange+8
postfit_color = kGreen+2

crmap = {
    'we':{'mc':'WJets','leg':'W #rightarrow e#nu'},
    'wm':{'mc':'WJets','leg':'W #rightarrow #mu#nu'},
    'ze':{'mc':'DYJets','leg':'Z #rightarrow ee'},
    'zm':{'mc':'DYJets','leg':'Z #rightarrow #mu#mu'},
    'ga':{'mc':'GJets','leg':'#gamma + jets'}
}
def loop_iterator(iterator):
  object = iterator.Next()
  while object:
    yield object
    object = iterator.Next()

def iter_collection(rooAbsCollection):
  iterator = rooAbsCollection.createIterator()
  return loop_iterator(iterator)
def getOtherBkg(cr,tfile):
    bkg = None
    tdir = tfile.Get('shapes_prefit/%s' % cr)
    for mc in mclist:
        if crmap[cr]['mc'] in mc: continue
        tmp = tdir.Get('%s' % mc)
        if tmp == None: continue
        if bkg is None: bkg = tmp
        else:           bkg.Add(tmp)
    bkg.SetFillColor(kOrange-2)
    bkg.SetLineColor(kBlack)
    return bkg
def plotCR(cr,tfile,info):
    prefit_hs = tfile.Get('shapes_prefit/%s/total_background' % (cr))
    postfit_hs = tfile.Get('shapes_fit_b/%s/total_background' % (cr))
    data_graph = tfile.Get('shapes_prefit/%s/data' % cr)
    nuisances = tfile.Get('nuisances_prefit')

    other_bkg = getOtherBkg(cr,tfile)

    c = TCanvas("c", "canvas",800,800);
    gStyle.SetOptStat(0);
    gStyle.SetLegendBorderSize(0);

    pad1 = TPad("pad1","pad1",0.,0.33,1.0,1.0)
    pad1.Draw(); pad1.cd()
    pad1.SetLogy()
    pad1.SetBottomMargin(0)

    prefit_hs.Draw("hist"); fit_style(prefit_hs,prefit_color);
    set_bounds(prefit_hs)
    postfit_hs.Draw("hist same"); fit_style(postfit_hs,postfit_color)
    other_bkg.Draw("hist same")
    data_graph.Draw("pex0 same"); data_style(data_graph)
    prefit_hs.Draw("Axis same")

    leg = getLegend()
    leg.AddEntry(data_graph,"Data","lp")
    leg.AddEntry(postfit_hs,"Post-fit (%s)" % crmap[cr]['leg'],'f')
    leg.AddEntry(prefit_hs,"Pre-fit (%s)" % crmap[cr]['leg'],'f')
    leg.AddEntry(other_bkg,"Other Backgrounds",'f')
    leg.Draw()

    texCMS,texLumi = getCMSText(info.lumi_label,info.year)

    ##############################
    c.cd()
    pad2 = TPad("pad2","pad2",0.,0.,1.0,0.33)
    pad2.Draw(); pad2.cd()
    pad2.SetTopMargin(0)

    pad3 = TPad("pad3","pad3",0.,0.65,1.,1.)
    pad3.Draw(); pad3.cd()
    pad3.SetTopMargin(0); pad3.SetBottomMargin(0)
    
    data_hs = makeHistogram(data_graph,prefit_hs)

    prefit_ratio = data_hs.Clone('prefit_ratio'); prefit_ratio.Divide(prefit_hs)
    postfit_ratio = data_hs.Clone('postfit_ratio'); postfit_ratio.Divide(postfit_hs)

    prefit_ratio.Draw('pe'); ratio_style(prefit_ratio,prefit_color)
    postfit_ratio.Draw('pesame'); ratio_style(postfit_ratio,postfit_color)

    ###############################
    pad2.cd()
    pad4 = TPad("pad4","pad4",0.,0.,1.,0.65)
    pad4.Draw(); pad4.cd()
    pad4.SetTopMargin(0);
    pad4.SetBottomMargin(0.5)
    
    sigma_pull = SigmaPull(data_hs,postfit_hs)
    sigma_pull.Draw('hist'); pull_style(sigma_pull,postfit_color)
    xname = sigma_pull.GetXaxis().GetTitle().replace("(","[").replace(")","]")
    sigma_pull.GetXaxis().SetTitle( xname )

    ##############################

    outdir = outdir_base % info.year
    outname = 'fit_CRonly_%s_%s.png' % (cr,info.sysdir)
    outvar = '%s/%s/' % (outdir,info.variable)
    if not os.path.isdir(outvar): os.mkdir(outvar)
    outsys = '%s/%s' % (outvar,info.sysdir)
    if not os.path.isdir(outsys): os.mkdir(outsys)
    output = '%s/%s' % (outsys,outname)
    c.SaveAs(output)
def plotCRFit(path):
  global crmap
  if 'nCR' in path: return
  cwd = os.getcwd()
  info = SysInfo(path)
  os.chdir('%s/cr_fit' % path)
  tfile = TFile.Open("fitDiagnostics_fit_CRonly_result.root")
  crlist = [ crdir.GetName() for crdir in tfile.Get('shapes_prefit').GetListOfKeys() if any( cr in crdir.GetName() for cr in crmap ) ]
  for cr in crlist:
    crmap[cr] = crmap[cr.split('_')[0]]
    plotCR(cr,tfile,info)
  os.chdir(cwd)
##############################################################################
def getargs():
    def directory(arg):
        if os.path.isdir(arg): return arg
        raise ValueError()
    parser = ArgumentParser(description='Run all avaiable limits in specified directory')
    parser.add_argument("-d","--dir",help='Specify the directory to run limits in',nargs='+',action='store',type=directory,required=True)
    try: args = parser.parse_args()
    except:
        parser.print_help()
        exit()
    return args
##############################################################################
if __name__ == "__main__":
    args = getargs()
    for dir in args.dir: plotCRFit(dir)
