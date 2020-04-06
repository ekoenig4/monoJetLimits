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

# gROOT.SetBatch(1)

outdir_base = "/afs/hep.wisc.edu/home/ekoenig4/public_html/MonoJet/Plots%s/ExpectedLimits/"
def getTFNames(w):
  functions = w.allFunctions().selectByName("func_r_*_bin0")
  return [ function.GetName().replace("_bin0","") for function in setiter(functions) ]
def getInverse(function):
  formula = function.formula()
  arglist = RooArgList()
  npar = function.getVariables().getSize()
  for i in range(npar): arglist.add( function.getParameter(i) )
  inverse = RooFormulaVar("inv_"+function.GetName(),"Inverse "+function.GetTitle(),"1/(%s)"%formula.GetTitle(),arglist)
  inverse.arglist = arglist
  return inverse
def makePDF(w,tfname,inverse=False):
  functions = w.allFunctions().selectByName(tfname+"*")
  pdfargs = RooArgList()
  pdflist = []
  for function in setiter(functions):
    if inverse: function = getInverse(function)
    pdfargs.add(function)
    pdflist.append(function)
  template = w.allPdfs().first()
  var = w.var('recoil')
  htemp = template.createHistogram('recoil')
  pdf = RooParametricHist(tfname,tfname,var,pdfargs,htemp)
  pdf.pdflist = pdflist
  h =pdf.createHistogram('recoil').Rebin(2)
  clone = h.Clone()
  # h.Scale(52)
  for i in range(2): h.Divide(clone)
  h.Draw('hist')
  raw_input()
  exit()
##############################################################################
def getargs():
  def workspace(arg):
    tfile = TFile(arg)
    if not tfile: raise ValueError()
    ws = tfile.Get("w")
    if not ws: raise ValueError()
    return ws
  parser = ArgumentParser(description='Run all avaiable limits in specified directory')
  parser.add_argument("-w","--workspace",type=workspace,required=True)
  try: args = parser.parse_args()
  except:
    parser.print_help()
    exit()
  return args
##############################################################################
if __name__ == "__main__":
  args = getargs()
  w = args.workspace
  tflist = getTFNames(w)

  for tfname in tflist: makePDF(w,tfname)
