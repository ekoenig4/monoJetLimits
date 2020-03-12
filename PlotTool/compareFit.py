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

bumap = {
  "sr":"monojet_%s_signal",
  "we":"monojet_%s_singleel",
  "wm":"monojet_%s_singlemu",
  "ze":"monojet_%s_dielec",
  "zm":"monojet_%s_dimuon",
  "ga":"monojet_%s_photon"
}

prefit_color = kOrange+8
postfit_color = kGreen+2
other_color = kOrange-2

def loop_iterator(iterator):
  object = iterator.Next()
  while object:
    yield object
    object = iterator.Next()

def iter_collection(rooAbsCollection):
  iterator = rooAbsCollection.createIterator()
  return loop_iterator(iterator)
def compareFit(cr,uw_fit,bu_fit,info):
  uw_fit.getRegion(cr)
  c,y=cr.split("_")
  bu_fit.getRegion(bumap[c]%y)
  
  c = TCanvas("c", "canvas",800,800);
  gStyle.SetOptStat(0);
  gStyle.SetLegendBorderSize(0);
  
  pad1 = TPad("pad1","pad1",0.,0.33,1.0,1.0)
  pad1.Draw(); pad1.cd()
  pad1.SetLogy()
  pad1.SetBottomMargin(0)

  uw_postfit = uw_fit.postfit_hs
  bu_postfit = bu_fit.postfit_hs

  data_style(bu_postfit)
  fit_style(uw_postfit,kRed)

  uw_postfit.Draw("hist")
  bu_postfit.Draw("pex0same")
  
  leg = getLegend()
  leg.AddEntry(bu_postfit,"BU Post-fit (%s)" % regionmap[cr]['leg'],'p')
  leg.AddEntry(uw_postfit,"UW Post-fit (%s)" % regionmap[cr]['leg'],'l')
  leg.Draw()
  
  texCMS,texLumi = getCMSText(info.lumi_label,info.year)
  
  ##############################
  c.cd()
  pad2 = TPad("pad2","pad2",0.,0.,1.0,0.33)
  pad2.Draw(); pad2.cd()
  pad2.SetTopMargin(0)
  pad2.SetBottomMargin(0.35)

  postfit_ratio = bu_postfit.Clone("postfit_ratio")
  postfit_ratio.Divide(uw_postfit)

  postfit_ratio.GetXaxis().SetTitle( uw_postfit.GetXaxis().GetTitle() )
  postfit_ratio.Draw('pex0same'); ratio_style(postfit_ratio,kBlack,name="BU/UW")
  postfit_ratio.GetYaxis().SetTitleSize(0.1)
  postfit_ratio.GetYaxis().SetLabelSize(0.08)
  postfit_ratio.GetYaxis().SetTitleOffset(0.4)
  
  ##############################
  
  outdir = outdir_base % info.year
  outname = 'fit_compare_%s_%s.png' % (cr,info.sysdir)
  outvar = '%s/%s/' % (outdir,info.variable)
  outsys = '%s/%s_OldSetup/BU_Comparison/' % (outvar,info.sysdir)
  if not os.path.isdir(outsys): os.makedirs(outsys)
  output = '%s/%s' % (outsys,outname)
  c.SaveAs(output)
def compareSysfile(uw_dir,bu_file):
  global regionmap
  cwd = os.getcwd()
  info = SysInfo(uw_dir)
  uw_fit = FitFile("%s/cr_fit/fitDiagnostics_fit_CRonly_result.root"%info.cwd)
  bu_fit = FitFile(bu_file)
  crlist = [ crdir.GetName() for crdir in uw_fit.Get('shapes_prefit').GetListOfKeys() if any( cr in crdir.GetName() for cr in regionmap ) ]
  for cr in crlist:
    regionmap[cr] = regionmap[cr.split('_')[0]]
    compareFit(cr,uw_fit,bu_fit,info)
  os.chdir(cwd)
##############################################################################
def getargs():
    parser = ArgumentParser(description='Compare fit files')
    parser.add_argument("-f","--files",help='Specify the files to get fits from',nargs='+',required=True)
    try: args = parser.parse_args()
    except:
        parser.print_help()
        exit()
    return args
##############################################################################
if __name__ == "__main__":
    args = getargs()
    compareSysfile(args.files[0],args.files[1])
