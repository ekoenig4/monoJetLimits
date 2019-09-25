#!/usr/bin/env python

from ROOT import *
from Datacard import Datacard
import re

def loop_iterator(iterator):
  object = iterator.Next()
  while object:
    yield object
    object = iterator.Next()

def iter_collection(rooAbsCollection):
  iterator = rooAbsCollection.createIterator()
  return loop_iterator(iterator)

mclist = ['ZJets','WJets','DiBoson','GJets','TTJets','DYJets','QCD']

signal = 'Mx10_Mv1000'

channels = {
  'sr':
  {
    'mc':[signal] + mclist,
    'transfer':[r'^zoverw_\S*$',r'^WJets_sr_\S*_Runc$']
  },
  'e':
  {
    'mc':mclist,
    'transfer':[r'^WJets_e_\S*_Runc$']
  },
  'm':
  {
    'mc':mclist,
    'transfer':[r'^WJets_m_\S*_Runc$']
  },
  'ee':
  {
    'mc':mclist,
    'transfer':[r'^DYJets_ee_\S*_Runc$']
  },
  'mm':
  {
    'mc':mclist,
    'transfer':[r'^DYJets_mm_\S*_Runc$']
  }
}

def makeCard(wsfname,ch,info,ws=None):
  if ws == None:
    rfile = TFile.Open(wsfname)
    ws = rfile.Get('w')
  print 'Making datacard_%s' % ch
  mclist = info['mc']
  transfers = info['transfer']

  def validHist(ch,histname): return any( ch == w for w in histname.split('_') )
  ch_hist = { hist.GetName():hist for hist in ws.allData() if validHist(ch,hist.GetName()) }
  ch_vars = {}
  wsvar = ws.allVars()
  for var in iter_collection(wsvar):
    name = var.GetName()
    for transfer in transfers:
      if re.search(transfer,name) != None:
        ch_vars[name] = var
        
  ch_card = Datacard(ch)
  ch_card.setObservation(shape=(wsfname,'w:data_obs_%s' % ch))
  for mc in mclist:
    proc = '%s_%s' % (mc,ch)
    if proc not in ch_hist: continue
    hist = ch_hist[proc]
    if mc == signal: ch_card.addSignal(mc,shape=(wsfname,'w:%s' % proc))
    else:              ch_card.addBkg(mc,shape=(wsfname,'w:%s' % proc))
    
    ch_card.addNuisance(mc,'lumi','lnN',1.026)
    ch_card.addNuisance(mc,'et_trigg','lnN',1.01)
    ch_card.addNuisance(mc,'bjet_veto','lnN',1.02)
    variations = [ key.replace('%s_' % proc ,'').replace('Up','') for key in ch_hist if re.search(r'%s_%s_\S*Up$' % (mc,ch),key) ]
    for variation in variations: ch_card.addNuisance(mc,variation,'shape',1)
  #####
  ch_card.addNuisance('ZJets','ZJets_EWK','lnN',1.10)
  ch_card.addNuisance('WJets','WJets_EWK','lnN',1.15)

  # Remove possibly uneeded nuisance parameters from certain processes
  for process in ('WJets','ZJets'):
    ch_card.removeNuisance(process,'JES')
    
  for transfer in ch_vars: ch_card.addTransfer(transfer)
  ch_card.write()

def getWorkspace(fname):
  rfile = TFile.Open(fname)
  ws = rfile.Get('w')
  return ws
      
def createDatacards(input): 
  ws = getWorkspace(input)

  for ch,info in channels.iteritems():
    makeCard(input,ch,info,ws=ws)
        

if __name__ == "__main__":
  wsfname = 'workspace.root'
  createDatacards(wsfname)