#!/usr/bin/env python

from ROOT import *
from Datacard import Datacard
from lnNlist import lnNlist
from Parser import parser
import SignalInfo
import re
import os

cat_list = ["sr","we","wm","ze","zm","ga"]

parser.add_argument("--include",help="List of categories to include in datacard",nargs="+",choices=cat_list,default=cat_list)
parser.add_argument("--remove",help="Remove categories from datacards",nargs="+",choices=cat_list,default=[])
parser.add_argument("--freeze",help="Freeze nuisance parameters from begin included in datacards",nargs="+",default=[],type=lambda arg:re.compile("^"+arg+"$"))

def channel_order(ch1,ch2,ch_order=list(cat_list)):
    for i,ch in enumerate(ch_order):
        if ch in ch1: i1 = i
        if ch in ch2: i2 = i
    if i1 < i2: return -1
    elif i1 == i2:
            y1 = re.findall('\d\d\d\d',ch1)
            y2 = re.findall('\d\d\d\d',ch2)
            if any(y1) and any(y2):
                y1 = int(y1[0]); y2 = int(y2[0])
                if y1 < y2: return -1
    return 1
  
datadriven=['ZJets','WJets','DYJets','GJets']
signalmap = { }

frozen_params = set()
signal = []
#for my_Mchi,my_Mphi in my_mass_map.iteritems():
#    for Mphi_point in range(len(my_Mphi)):
#        name_string = 'axial_Mchi%s_Mphi%s'%(my_Mchi,my_Mphi[Mphi_point])
#        signal.append(name_string)
#print signal
#signal = ['axial']
signal = ["zprime_Mchi1_Mphi100"]
#signal = ["ggh","vbf","wh","zh"]
# signal = ["zprime"]
signalmap = { re.compile(sig):sig for sig in signal }

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
def getVars(ws,tfmodel):
  if tfmodel is None: return []
  obs = RooArgSet(ws.allVars().first())
  params = tfmodel.getParameters(obs).selectByAttrib("nuisance",True)
  return [ param.GetName() for param in iter_collection(params) ]
def getVariations(ch,proc): return [ hist.replace("%s_%s_"%(proc,ch.channel),"").replace("Up","") for hist in ch.hists if re.match('^'+proc,hist) and 'Up' in hist ]

def Add_lnN(card,proc,isSignal):
  region,year = card.channel.split("_")
  for lnN in lnNlist:
    if any( pattern.match(lnN.name) for pattern in parser.args.freeze ):
      frozen_params.add(lnN.name)
      continue
    name,value = lnN.get(proc.replace("_model",""),region,year)
    if name is None: continue
    card.addNuisance(proc.replace("_model",""),name,'lnN',value)
def Add_Shape(card,proc,nuisances):
  variations = getVariations(card,proc)
  for nuisance in nuisances:
    if any( pattern.match(nuisance) for pattern in parser.args.freeze ): 
      frozen_params.add(nuisance)
      continue
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
    if any( pattern.match(tf) for pattern in parser.args.freeze ):
      frozen_params.add(tf)
      continue
    card.addTransfer(tf)
def MakeCard(ws,ch,tf="",signal=[],useModel=True):
  print "Writing datacard_%s" % ch
  proclist = signal + ['ZJets','WJets','DYJets','GJets','DiBoson','TTJets','QCD']
  ch_card = Datacard(ch,ws)
  ch_card.hists = getHists(ws,ch)
  ch_card.pdfs = getPDFs(ws,ch)
  tfmodel = None
  if "%s_%s"%(tf,ch) in ch_card.pdfs: tfmodel = ws.pdf("%s_%s"%(tf,ch))
  ch_card.vars = getVars(ws,tfmodel)
  
  ch_card.setObservation(shape='data_obs_%s'%ch)
  for proc in proclist: AddProc(ch_card,proc,proc in signal,useModel=useModel)
  AddTF(ch_card,tf,useModel)
  ch_card.write()
  return

cardmap = {
  "sr":"WJets_model",
  "we":"WJets_model",
  "wm":"WJets_model",
  "ze":"DYJets_model",
  "zm":"DYJets_model",
  "ga":"GJets_model"
}
def createDatacards(wsfname,year):
  parser.parse_args()
  frozen_params.clear()
  
  input = TFile(wsfname)
  ws = input.Get("w")
  ws.fname = input.GetName()

  for datacard in os.listdir("."):
    if "datacard" in datacard:
      os.remove(datacard)

  chlist = list(parser.args.include)
  if year == "2016": chlist.remove("ga")
  for ch in parser.args.remove:
    if ch in chlist: chlist.remove(ch)
  chlist.sort(channel_order)

  signalmap.update( {re.compile(signal):signal for signal in parser.args.signal} )

  for ch in chlist:
    siglist = [] if ch != "sr" else ["zprime_Mchi1_Mphi100"]#parser.args.signal
    MakeCard(ws,"%s_%s"%(ch,year),cardmap[ch],signal=siglist)

  if any(frozen_params):
    print "Frozen Parameters:"
    for param in frozen_params:
      print "\t",param
    print
  return [ "datacard_%s_%s" % (ch,year) for ch in chlist ]
if __name__ == "__main__":
  input = TFile("workspace.root")
  ws = input.Get("w")
  ws.fname = input.GetName()
  MakeCard(ws,'sr_2017',('WJets_model','wsr_to_zsr'),['Axial_Mchi1_Mphi1000'])
