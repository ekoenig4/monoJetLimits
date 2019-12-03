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

mclist = ['ZJets','WJets','DiBoson','GJets','TTJets','DYJets','QCD']

signal = 'Mx1_Mv1000'

channels = {
  'sr':
  {
    'mc':[signal] + mclist,
    'transfer':[r'^ZoverW_\S*$'],
    'isCR':False
  },
  'we':
  {
    'mc':mclist,
    'transfer':[r'^SRoverCR_we_\S*_Runc$'],
    'isCR':True
  },
  'wm':
  {
    'mc':mclist,
    'transfer':[r'^SRoverCR_wm_\S*_Runc$'],
    'isCR':True
  },
  'ze':
  {
    'mc':mclist,
    'transfer':[r'^SRoverCR_ze_\S*_Runc$'],
    'isCR':True
  },
  'zm':
  {
    'mc':mclist,
    'transfer':[r'^SRoverCR_zm_\S*_Runc$'],
    'isCR':True
  }
}
zw_variations = ["QCD_Scale","QCD_Shape","QCD_Proc","NNLO_EWK","NNLO_Miss","NNLO_Sud","QCD_EWK_Mix"]

def isZWVariation(variation,nCR):
  if nCR: return False
  return any( zw in variation for zw in zw_variations )
def getVariations(mc,ch,ch_hist):
  procname = '%s_%s' % (mc,ch)
  return [ key[len(procname)+1:].replace('Up','') for key in ch_hist if re.search('%s_\S*Up$' % procname,key) ]

def makeCard(wsfname,ch,info,options,ws=None):
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

    if options.nSYS: continue
    ch_card.addNuisance(mc,'lumi','lnN',1.026)
    ch_card.addNuisance(mc,'et_trigg','lnN',1.01)
    ch_card.addNuisance(mc,'bjet_veto','lnN',1.02)
    variations = getVariations(mc,ch,ch_hist)
    for variation in variations:
      if isZWVariation(variation,options.nCR): continue
      if options.nSTAT and re.search('bin\d+_stat',variation): continue
      if options.nPFU and 'PFU' in variation: continue
      if options.nJES and 'JES' in variation: continue
      ch_card.addNuisance(mc,variation,'shape',1)
  #####
  # if not options.no_sys:
  #   ch_card.addNuisance('ZJets','ZJets_EWK','lnN',1.10)
  #   ch_card.addNuisance('WJets','WJets_EWK','lnN',1.15)

  # Remove possibly uneeded nuisance parameters from certain processes
  for process in ('WJets','ZJets'):
    ch_card.removeNuisance(process,'JES')

  for transfer in ch_vars:
    if options.nCR or options.nTRAN: continue
    if 'Runc' not in transfer and options.nSYS: continue
    ch_card.addTransfer(transfer)
  ch_card.write()

def getWorkspace(fname):
  rfile = TFile.Open(fname)
  ws = rfile.Get('w')
  return ws
      
def createDatacards(input,options):
  cwd = os.getcwd()
  ws = getWorkspace(input)
  for ch,info in channels.iteritems():
    if ch != 'sr' and options.nCR: continue
    makeCard(input,ch,info,options,ws=ws)
  os.chdir(cwd)

if __name__ == "__main__":
  wsfname = 'workspace.root'
  createDatacards(wsfname)
