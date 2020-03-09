#!/usr/bin/env python

from ROOT import *
from Datacard import Datacard
import re
import os

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
  return [ var.GetName() for var in iter_collection(wsvars) if ch in var.GetName() and any(re.match('^'+t,var.GetName()) for t in tf) ]
def getVariations(ch,proc): return [ hist.replace("%s_%s_"%(proc,ch.channel),"").replace("Up","") for hist in ch.hists if re.match('^'+proc,hist) and 'Up' in hist ]

def Add_lnN(card,proc,isSignal,datadriven):
  if proc not in datadriven: card.addNuisance(proc,'lumi','lnN',1.026)
  card.addNuisance(proc,'bjet_veto','lnN',1.06 if proc is 'TTJets' else 1.02)
  if proc is 'TTJets':
    card.addNuisance(proc,'top_pt_reweight','lnN',1.1)
    card.addNuisance(proc,'top_norm','lnN',1.1)
  if proc is 'DiBoson':
    card.addNuisance(proc,'diboson_norm','lnN',1.2)

  if 'sr' in card.channel:
    card.addNuisance(proc,'met_trig','lnN',1.01)
    if proc is 'DYJets':
      card.addNuisance(proc,'zll_norm','lnN',1.2)
    if proc is 'GJets':
      card.addNuisance(proc,'gjets_norm','lnN',1.2)
  
  if any( ch in card.channel for ch in ('we','ze') ):
    card.addNuisance(proc,'ele_trig','lnN',1.01)
    card.addNuisance(proc,'ele_reco','lnN',1.01)
    card.addNuisance(proc,'ele_id','lnN',1.02)

  if any( ch in card.channel for ch in ('wm','wm') ):
    card.addNuisance(proc,'met_trig','lnN',1.01)
    card.addNuisance(proc,'muon_reco','lnN',1.01)
    card.addNuisance(proc,'muon_id','lnN',1.01)

  if 'ga' in card.channel:
    card.addNuisance(proc,'pho_trig','lnN',1.01)
    card.addNuisance(proc,'pho_id','lnN',1.02)
    if proc is 'QCD':
      card.addNuisance(proc,'pho_purity','lnN',1.4)
def Add_Shape(card,proc,nuisances):
  variations = getVariations(card,proc)
  for nuisance in nuisances:
    if nuisance in variations:
      card.addNuisance(proc,nuisance,'shape',1)
def AddProc(card,proc,isSignal,nuisances=["JES","JER"],datadriven=['ZJets','WJets','DYJets','GJets']):
  procname = "%s_%s" % (proc,card.channel)
  if not any( procname in hists for hists in (card.hists,card.pdfs) ): return
  if isSignal: card.addSignal(proc,shape="w:%s" % procname)
  else:
    rate = 1 if procname in card.pdfs else -1
    card.addBkg(proc,shape="w:%s" % procname,rate=rate)
  
  Add_lnN(card,proc,isSignal,datadriven)
  Add_Shape(card,proc,nuisances)
def AddTF(card,tf):
  for tf in card.vars:
    card.addTransfer(tf)
def MakeCard(ws,ch,tf=None,signal=[]):
  print "Writing datacard_%s" % ch
  proclist = signal + ['ZJets','WJets','DYJets','GJets','DiBoson','TTJets','QCD']
  ch_card = Datacard(ch,ws)
  ch_card.hists = getHists(ws,ch)
  ch_card.vars = getVars(ws,ch,tf)
  ch_card.pdfs = getPDFs(ws,ch)

  ch_card.setObservation(shape='w:data_obs_%s'%ch)
  for proc in proclist: AddProc(ch_card,proc,proc in signal)
  AddTF(ch_card,tf)
  ch_card.write()

signal = ['Axial_Mchi1_Mphi1000']
def createDatacards(wsfname,year,signal=signal):
  input = TFile(wsfname)
  ws = input.Get("w")
  ws.fname = input.GetName()

  MakeCard(ws,"sr_%s"%year,("WJets","wsr_to_zsr"),signal)
  MakeCard(ws,"we_%s"%year,("WJets","we_to_sr"))
  MakeCard(ws,"wm_%s"%year,("WJets","wm_to_sr"))
  MakeCard(ws,"ze_%s"%year,("DYJets","ze_to_sr"))
  MakeCard(ws,"zm_%s"%year,("DYJets","zm_to_sr"))
  MakeCard(ws,"ga_%s"%year,("GJets","ga_to_sr"))
  return [ "datacard_%s_%s" % (ch,year) for ch in ("sr","we","wm","ze","zm","ga")]
if __name__ == "__main__":
  input = TFile("workspace.root")
  ws = input.Get("w")
  ws.fname = input.GetName()
  MakeCard(ws,'sr_2017',('WJets','wsr_to_zsr'),['Axial_Mchi1_Mphi1000'])
