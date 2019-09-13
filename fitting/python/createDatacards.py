#!/usr/bin/env python

from ROOT import *
from Datacard import Datacard

def loop_iterator(iterator):
  object = iterator.Next()
  while object:
    yield object
    object = iterator.Next()

def iter_collection(rooAbsCollection):
  iterator = rooAbsCollection.createIterator()
  return loop_iterator(iterator)

mclist = ['ZJets','WJets','DiBoson','GJets','TTJets','DYJets','QCD']

channels = {
  'sr':
  {
    'mc':['signal'] + mclist,
    'transfer':'woverz'
  },
  'e':
  {
    'mc':mclist,
    'transfer':'WentoWen'
  },
  'm':
  {
    'mc':mclist,
    'transfer':'WmntoWmn'
  },
  'ee':
  {
    'mc':mclist,
    'transfer':'ZeetoZnn'
  },
  'mm':
  {
    'mc':mclist,
    'transfer':'ZmmtoZnn'
  }
}

def makeCard(wsfname,ch,info,ws=None):
  if ws == None:
    rfile = TFile.Open(wsfname)
    ws = rfile.Get('w')
  print 'Making datacard_%s' % ch
  mclist = info['mc']
  transfer = info['transfer']

  def validHist(ch,histname): return any( ch == w for w in histname.split('_') )
  ch_hist = { hist.GetName():hist for hist in ws.allData() if validHist(ch,hist.GetName()) }
  ch_vars = {}
  wsvar = ws.allVars()
  for var in iter_collection(wsvar):
    name = var.GetName()
    if ch in name and transfer in name and ('r_%s' % transfer) not in name:
      ch_vars[name] = var
        
  ch_card = Datacard(ch)
  ch_card.setObservation(shape=(wsfname,'w:data_obs_%s' % ch))
  for mc in mclist:
    proc = '%s_%s' % (mc,ch)
    if proc not in ch_hist: continue
    hist = ch_hist[proc]
    if mc == 'signal': ch_card.addSignal(mc,shape=(wsfname,'w:%s' % proc))
    else:              ch_card.addBkg(mc,shape=(wsfname,'w:%s' % proc))
    
    ch_card.addNuisance(mc,'lumi','lnN',1.026)
    ch_card.addNuisance(mc,'et_trigg','lnN',1.01)
    ch_card.addNuisance(mc,'bjet_veto','lnN',1.02)
    
    if mc == 'ZJets':   ch_card.addNuisance(mc,'EWK','lnN',1.10)
    elif mc == 'WJets': ch_card.addNuisance(mc,'EWK','lnN',1.15)
    
    variations = [ key.replace('%s_' % proc ,'').replace('Up','') for key in ch_hist if 'Up' in key and mc in key ]
    for variation in variations: ch_card.addNuisance(mc,variation,'shape',1)
  for transfer in ch_vars: ch_card.addTransfer(transfer)
  ch_card.write()
      
def createDatacards():
  wsfname = 'workspace.root'
  rfile = TFile.Open(wsfname)
  ws = rfile.Get('w')

  for ch,info in channels.iteritems():
    makeCard(wsfname,ch,info,ws=ws)
        

if __name__ == "__main__":
  createDatacards()
