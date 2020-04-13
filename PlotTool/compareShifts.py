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
from array import array

gROOT.SetBatch(1)
gStyle.SetOptStat(0)

outdir_base = "/afs/hep.wisc.edu/home/ekoenig4/public_html/MonoZprimeJet/Plots%s/ExpectedLimits/"

procmap = {
  "ZJets_sr_%s":"zjets_monojet_%s_signal",
  "WJets_sr_%s":"wjets_monojet_%s_signal",
  "DYJets_zm_%s":"zll_monojet_%s_dimuon",
  "DYJets_ze_%s":"zll_monojet_%s_dielec",
  "WJets_we_%s":"wjets_monojet_%s_singleel",
  "WJets_wm_%s":"wjets_monojet_%s_singlemu",
  "GJets_ga_%s":"gjets_monojet_%s_photon"
}

nuisancemap = {
  "WJets_model_sr_%s_stat":"monojet_%s_stat_error_wzCR",
  "wsr_to_zsr_NNLO_Miss_zsr":"nnlomissZ",
  "wsr_to_zsr_NNLO_Miss_wsr":"nnlomissW",
  "wsr_to_zsr_NNLO_Sud_zsr":"sudakovZ",
  "wsr_to_zsr_NNLO_Sud_wsr":"sudakovW",
  "wsr_to_zsr_NNLO_EWK":"wewk",
  "wsr_to_zsr_QCD_Proc":"wqcdprocess",
  "wsr_to_zsr_QCD_Scale":"wqcd",
  "wsr_to_zsr_QCD_Shape":"wqcdshape",
  "wsr_to_zsr_PDF":"wpdf",
  "wsr_to_zsr_QCD_EWK_Mix":"wcross",
  "WJets_model_we_%s_stat":"monojet_%s_stat_error_singleelectronCR",
  "WJets_model_wm_%s_stat":"monojet_%s_stat_error_singlemuonCR",
  "DYJets_model_ze_%s_stat":"monojet_%s_stat_error_dielectronCR",
  "DYJets_model_zm_%s_stat":"monojet_%s_stat_error_dimuonCR",
  "GJets_model_ga_%s_stat":"monojet_%s_stat_error_photonCR",
  "ga_to_sr_NNLO_Miss_sr":"nnlomissZ",
  "ga_to_sr_NNLO_Miss_ga":"nnlomissG",
  "ga_to_sr_NNLO_Sud_sr":"sudakovZ",
  "ga_to_sr_NNLO_Sud_ga":"sudakovG",
  "ga_to_sr_NNLO_EWK":"ewk",
  "ga_to_sr_QCD_Proc":"qcdprocess",
  "ga_to_sr_QCD_Scale":"qcd",
  "ga_to_sr_QCD_Shape":"qcdshape",
  "ga_to_sr_PDF":"pdf",
  "ga_to_sr_QCD_EWK_Mix":"cross",
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
def compareNuisance(process,nuisance,uw,bu):
  uw_nuis,bu_nuis = nuisance
  c_uw = uw.Get(uw_nuis)
  c_bu = bu.Get(bu_nuis)

  uw_up,uw_dn = c_uw.GetPrimitive(uw_nuis+"shiftUp__recoil"),c_uw.GetPrimitive(uw_nuis+"shiftDn__recoil")
  bu_up,bu_dn = c_bu.GetPrimitive(bu_nuis+"shiftUp__met_monojet_2017"),c_bu.GetPrimitive(bu_nuis+"shiftDn__met_monojet_2017")
  # def getTGraph(up,dn):
  #   npoints = up.GetNbinsX()
  #   x,exl,exh = [],[],[]
  #   y,eyl,eyh = [],[],[]
  #   for i in range(npoints):
  #     x.append(up.GetXaxis().GetBinCenter(i+1)); y.append(1)
  #     exl.append(0); exh.append(0)
  #     eyl.append( abs(uw_dn[i+1] - 1) )
  #     eyh.append( abs(uw_up[i+1] - 1) )
  #   return TGraphAsymmErrors(npoints,array('f',x),array('f',y),array('f',exl),array('f',exh),array('f',eyl),array('f',eyh))
  # uw_graph = getTGraph(uw_up,uw_dn)
  # bu_graph = getTGraph(bu_up,bu_dn)

  canvas = TCanvas(uw_nuis)
  # multi = TMultiGraph()

  def uw_style(hs):
    hs.SetLineColor(kRed);
    hs.SetLineWidth(1504);
    # hs.SetFillStyle(3005);
    # hs.SetFillColor(2);
  def bu_style(hs):
    hs.SetLineColor(kBlue);
    hs.SetLineWidth(2);
    # hs.SetFillStyle(3005);
    # hs.SetFillColor(9);

  binlist = list(uw_up)[1:-1] + list(uw_dn)[1:-1] + list(bu_up)[1:-1] + list(bu_dn)[1:-1]
  ymax = max(binlist)
  ymin = min(binlist)
  diff = ymax - ymin
  for h_uw in (uw_up,uw_dn): uw_style(h_uw)
  for h_bu in (bu_up,bu_dn): bu_style(h_bu)
  uw_up.Draw("hist")
  uw_dn.Draw("histsame")
  bu_up.Draw("histsame")
  bu_dn.Draw("histsame")
  uw_up.GetYaxis().SetRangeUser(ymin - diff,ymax + diff)
  uw_up.GetYaxis().SetTitle(uw_nuis)
  uw_up.SetTitle("")

  legend = TLegend(0.5,0.7,0.7,0.9)
  legend.AddEntry(uw_up,"UW","l")
  legend.AddEntry(bu_up,"BU","l")
  legend.Draw()
  
  outbase = "/afs/hep.wisc.edu/home/ekoenig4/public_html/MonoZprimeJet/test/BU_Fit/Nuisances/%s/" % process
  if not os.path.isdir(outbase): os.makedirs(outbase)
  canvas.SaveAs(outbase+uw_nuis+".png")
def compareProcess(process,uw,bu):
  uw_proc,bu_proc = process
  uw_dir = uw.GetDirectory(uw_proc)
  bu_dir = bu.GetDirectory(bu_proc)
  keylist = [ key.GetName() for key in uw_dir.GetListOfKeys() ]

  year = re.findall('\d\d\d\d',uw_proc)[0]
  for uw_key,bu_key in nuisancemap.iteritems():
      uwkey = uw_key
      if '%' in uwkey: uwkey = uw_key % year
      bukey = bu_key
      if '%' in bukey: bukey = bu_key % year
      if uwkey in keylist:
        compareNuisance(uw_proc,(uwkey,bukey),uw_dir,bu_dir)
def compareFiles(uw,bu):
  uw = TFile(uw)
  bu = TFile(bu)
  keylist = [ key.GetName() for key in uw.GetListOfKeys() ]
  for uwkey in keylist:
    print uwkey
    year = re.findall('\d\d\d\d',uwkey)[0]
    bukey = next( 'shapeBkg_'+bukey%year for key,bukey in procmap.iteritems() if key%year in uwkey )
    compareProcess((uwkey,bukey),uw,bu)
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
    compareFiles(args.files[0],args.files[1])
