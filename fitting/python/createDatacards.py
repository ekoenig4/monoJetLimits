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

mclist = ['signal','ZJets','WJets','DiBoson','GJets','TTJets','DYJets','QCD']

wsfname = 'workspace.root'

rfile = TFile.Open(wsfname)
ws = rfile.Get('w')

ch = 'sr'

sr_hist = { hist.GetName():hist for hist in ws.allData() if ch in hist.GetName() }
sr_vars = {}
wsvar = ws.allVars()
for var in iter_collection(wsvar):
    name = var.GetName()
    if ch in name and 'Runc' in name:
        sr_vars[name] = var
        
sr_card = Datacard(ch)
sr_card.setObservation(shape=(wsfname,'w:data_obs_%s' % ch))
for mc in mclist:
    hist = sr_hist[mc+'_sr']
    if mc == 'signal': sr_card.addSignal(mc,shape=(wsfname,'w:%s_%s' % (mc,ch)))
    else:              sr_card.addBkg(mc,shape=(wsfname,'w:%s_%s' % (mc,ch)))

    sr_card.addNuisance(mc,'lumi','lnN',1.026)
    sr_card.addNuisance(mc,'et_trigg','lnN',1.01)
    sr_card.addNuisance(mc,'bjet_veto','lnN',1.02)

    if mc == 'ZJets':   sr_card.addNuisance(mc,'EWK','lnN',1.10)
    elif mc == 'WJets': sr_card.addNuisance(mc,'EWK','lnN',1.15)

    variations = [ key.replace('%s_%s_' % (mc,ch) ,'').replace('Up','') for key in sr_hist if 'Up' in key and mc in key ]
    for variation in variations:
        sr_card.addNuisance(mc,variation,'shape',1)
for transfer in sr_vars:
    sr_card.addTransfer(transfer)
        
sr_card.write()
