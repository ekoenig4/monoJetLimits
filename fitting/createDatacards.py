#!/usr/bin/env python

from ROOT import *
from Datacard import Datacard
from lnNlist import lnNlist
import re
import os

datadriven=['ZJets','WJets','DYJets','GJets']
signal = ['axial']
signalmap = {re.compile(r"axial"):"axial"}

def loop_iterator(iterator):
  object = iterator.Next()
  while object:
    yield object
    object = iterator.Next()

def iter_collection(rooAbsCollection):
  iterator = rooAbsCollection.createIterator()
  return loop_iterator(iterator)

def getPDFs(ws,ch): 
  wspdfs = ws.allPdfs()
  return [ pdf.GetName() for pdf in iter_collection(wspdfs) if ch in pdf.GetName() ]
def getHists(ws,ch):
  return [ hist.GetName() for hist in ws.allData() if ch in hist.GetName() ]
def getVars(ws,ch,tf):
  if tf is None: return []
  wsvars = ws.allVars()
  varlist = [ var.GetName() for var in iter_collection(wsvars) if any(re.match('^'+t,var.GetName()) for t in tf) ]
  return varlist
def getVariations(ch,proc): return [ hist.replace("%s_%s_"%(proc,ch.channel),"").replace("Up","") for hist in ch.hists if re.match('^'+proc,hist) and 'Up' in hist ]

def Add_lnN(card,proc,isSignal):
  region,year = card.channel.split("_")
  for lnN in lnNlist:
    name,value = lnN.get(proc.replace("_model",""),region,year)
    if name is None: continue
    card.addNuisance(proc.replace("_model",""),name,'lnN',value)
def Add_Shape(card,proc,nuisances):
  variations = getVariations(card,proc)
  for nuisance in nuisances:
    if nuisance in variations:
      card.addNuisance(proc,nuisance,'shape',1)
def AddProc(card,proc,isSignal,nuisances=[],useModel=True):
  procname = "%s_%s" % (proc,card.channel)
  if not any( procname in hists for hists in (card.hists,card.pdfs) ): return
  hasModel = any( proc in pdf for pdf in card.pdfs )
  if isSignal:
    for pattern,alt in signalmap.iteritems():
      if pattern.match(proc): proc = alt
    card.addSignal(proc,shape=procname)
  elif useModel and hasModel:
    procname = "%s_model_%s" % (proc,card.channel)
    card.addModel(proc,shape=procname,rate=1)
    proc = "%s_model" % proc
  else:
    card.addBkg(proc,shape=procname)
  
  Add_lnN(card,proc,isSignal)
  Add_Shape(card,proc,nuisances)
def AddTF(card,tf,useModel):
  if not useModel: return
  for tf in card.vars:
    card.addTransfer(tf)
def MakeCard(ws,ch,tf=None,signal=[],useModel=True):
  print "Writing datacard_%s" % ch
  proclist = signal + ['ZJets','WJets','DYJets','GJets','DiBoson','TTJets','QCD']
  ch_card = Datacard(ch,ws)
  ch_card.hists = getHists(ws,ch)
  ch_card.vars = getVars(ws,ch,tf)
  ch_card.pdfs = getPDFs(ws,ch)
  
  ch_card.setObservation(shape='data_obs_%s'%ch)
  for proc in proclist: AddProc(ch_card,proc,proc in signal,useModel=useModel)
  AddTF(ch_card,tf,useModel)
  ch_card.write()

def createDatacards(wsfname,year,signal=signal):
  input = TFile(wsfname)
  ws = input.Get("w")
  ws.fname = input.GetName()

  MakeCard(ws,"sr_%s"%year,("WJets_model","wsr_to_zsr"),signal)
  MakeCard(ws,"we_%s"%year,("WJets_model","we_to_sr"))
  MakeCard(ws,"wm_%s"%year,("WJets_model","wm_to_sr"))
  MakeCard(ws,"ze_%s"%year,("DYJets_model","ze_to_sr"))
  MakeCard(ws,"zm_%s"%year,("DYJets_model","zm_to_sr"))
  MakeCard(ws,"ga_%s"%year,("GJets_model","ga_to_sr"))
  return [ "datacard_%s_%s" % (ch,year) for ch in ("sr","we","wm","ze","zm","ga")]
if __name__ == "__main__":
  input = TFile("workspace.root")
  ws = input.Get("w")
  ws.fname = input.GetName()
  MakeCard(ws,'sr_2017',('WJets_model','wsr_to_zsr'),['Axial_Mchi1_Mphi1000'])
