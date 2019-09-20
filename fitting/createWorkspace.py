#!/usr/bin/env python
from ROOT import *
from os import getenv
from Workspace import Workspace
import re

gSystem.Load("libHiggsAnalysisCombinedLimit.so")

mclist = ['ZJets','WJets','DYJets','TTJets','DiBoson','GJets','QCD']

def validShape(up,dn):
    return any( up[ibin] != dn[ibin] for ibin in range(1,up.GetNbinsX()+1) )

def validHisto(hs,total=0,threshold=0.2):
    return hs.Integral() > threshold*total

def addStat(dir,ws,hs,name=None):
    if name == None: name = hs.GetName()
    for ibin in range(1,hs.GetNbinsX()+1):
        up = hs.Clone("%s_%s_histBinUp" % (hs.GetName(),dir.GetName()))
        dn = hs.Clone("%s_%s_histBinDown" % (hs.GetName(),dir.GetName()))
        up[ibin] = up[ibin] + up.GetBinError(ibin)
        dn[ibin] = max( 0.01*dn[ibin],dn[ibin] - dn.GetBinError(ibin))

        ws.addTemplate("%s_%s_%s%sBin%iUp" % (hs.GetName(),dir.GetName(),name,dir.GetName(),ibin),up)
        ws.addTemplate("%s_%s_%s%sBin%iDown" % (hs.GetName(),dir.GetName(),name,dir.GetName(),ibin),dn)

def addMC(dir,ws,variations):
    print 'Processing %s MC' % dir.GetName()
    total_bkg = dir.Get('sumOfBkg').Integral()
    for mc in mclist:
        print 'Adding %s Process' % mc
        mc_hs = dir.Get(mc)
        if not validHisto(mc_hs): continue
        ws.addTemplate("%s_%s" % (mc,dir.GetName()),dir.Get(mc))
        for variation in variations:
            mc_up = dir.Get("%s_%sUp" % (mc,variation))
            mc_dn = dir.Get("%s_%sDown" % (mc,variation))
            if not validShape(mc_up,mc_dn): continue
            ws.addTemplate("%s_%s_%sUp" % (mc,dir.GetName(),variation),mc_up)
            ws.addTemplate("%s_%s_%sDown" % (mc,dir.GetName(),variation),mc_dn)
        if not validHisto(mc_hs,total=total_bkg): continue
        addStat(dir,ws,mc_hs)

def getFractionalShift(norm,up,dn):
    sh = up.Clone( up.GetName().replace('Up','FractionalShifts') )
    for ibin in range(1,sh.GetNbinsX()+1):
        if norm[ibin] != 0:
            upshift = up[ibin]/norm[ibin] - 1.
            dnshift = dn[ibin]/norm[ibin] - 1.
            shiftEnvelope = max( abs(upshift),abs(dnshift) )
        else: shiftEnvelope = 0
        sh[ibin] = shiftEnvelope
    return sh

def ZWLink(dir,ws,variations,connect):
    print 'Processing %s Transfer Factors' % dir.GetName()
    zjet = dir.Get("ZJets")
    wjet = dir.Get("WJets")
    zbinlist = RooArgList()
    ws.makeBinList("ZJets_%s" % dir.GetName(),zjet,zbinlist)
    zwdir = dir.GetDirectory("zwlink"); zwdir.cd()
    woverz_hs = zwdir.Get("ZWlink")
    syslist = []
    for variation in variations:
        if variation == 'JES': continue
        for process in ('WJets','ZJets'):
            woverz_up = zwdir.Get("ZWlink_%sUp_%s" % (variation,process))
            woverz_dn = zwdir.Get("ZWlink_%sDown_%s" % (variation,process))
            if not validShape(woverz_up,woverz_dn): continue
            woverz_sh = getFractionalShift(woverz_hs,woverz_up,woverz_dn)
            var = RooRealVar("zoverw_%s_%s_%s" % (dir.GetName(),process,variation),"",0.,-5.,-5.)
            syslist.append( {'var':var,'histo':woverz_sh} )
    wbinlist = RooArgList()
    if connect: ws.makeConnectedBinList("WJets_%s" % dir.GetName(),wjet,syslist,zbinlist,wbinlist)
    else:       ws.makeBinList("WJets_%s" % dir.GetName(),wjet,wbinlist)
    return zbinlist,wbinlist

def addSignal(dir,ws,variations,signals,isScaled=False):
    print 'Processing Signal'
    if type(signals) != list: signals = [signals]
    for signal in signals:
        signal_hs = dir.Get(signal)
        if isScaled:
            signal_yield = signal_hs.Integral()
            signal_multi = 80.0 / signal_yield # Normalize so that combine limits are close to 1
            signal_hs.Scale(signal_multi)
        ws.addTemplate('%s_%s' % (signal_hs.GetName(),dir.GetName()),signal_hs)
        for variation in variations:
            signal_up = dir.Get("%s_%sUp" % (signal,variation))
            signal_dn = dir.Get("%s_%sDown" % (signal,variation))
            if not validShape(signal_up,signal_dn): continue
            ws.addTemplate("%s_%s_%sUp" % (signal_hs.GetName(),dir.GetName(),variation),signal_up)
            ws.addTemplate("%s_%s_%sDown" % (signal_hs.GetName(),dir.GetName(),variation),signal_dn)
        addStat(dir,ws,signal_hs,name='signal')
            

def getSignalRegion(dir,rfile,ws,signal=None):
    print 'Processing sr'
    dir.cd()

    variations = [ key.GetName().replace('ZJets_','').replace('Up','')
                   for key in dir.GetListOfKeys()
                   if 'ZJets' in key.GetName() and 'Up' in key.GetName() ]
    
    data_obs = dir.Get('data_obs'); data_obs.SetDirectory(0)
    ws.addTemplate('data_obs_%s' % dir.GetName(),data_obs)

    nbins = data_obs.GetNbinsX()

    if signal != None:
        signals = [ key.GetName() for key in dir.GetListOfKeys() if re.search(signal,key.GetName()) ]
        addSignal(dir,ws,variations,signals)
        

    zbinlist,wbinlist = ZWLink(dir,ws,variations,True)

    addMC(dir,ws,variations)

    return zbinlist,wbinlist

def getLLTransfer(dir,ws,variations,zbinlist):
    print 'Processing %s Transfer Factors' % dir.GetName()
    tfdir = dir.GetDirectory("transfer"); tfdir.cd()
    covers_hs = tfdir.Get("ZJets")
    syslist = []
    for variation in variations:
        covers_up = tfdir.Get("ZJets_%sUp" % variation)
        covers_dn = tfdir.Get("ZJets_%sDown" % variation)
        if not validShape(covers_up,covers_dn): continue
        covers_sh = getFractionalShift(covers_hs,covers_up,covers_dn)
        var = RooRealVar("DYJets_%s_%s" % (dir.GetName(),variation),"",0.,-5.,-5.)
        syslist.append( {'var':var,'histo':covers_sh} )
    ws.makeConnectedBinList("DYJets_%s" % dir.GetName(),covers_hs,syslist,zbinlist)

def getLLCR(dir,rfile,ws,zbinlist):
    print 'Processing %s' % dir.GetName()
    dir.cd()

    variations = [ key.GetName().replace('ZJets_','').replace('Up','')
                   for key in dir.GetListOfKeys()
                   if 'ZJets' in key.GetName() and 'Up' in key.GetName() ]
    
    data_obs = dir.Get('data_obs'); data_obs.SetDirectory(0)
    ws.addTemplate('data_obs_%s' % dir.GetName(),data_obs)

    getLLTransfer(dir,ws,variations,zbinlist)

    addMC(dir,ws,variations)

def getLTransfer(dir,ws,variations,wbinlist):
    print 'Processing %s Transfer Factors' % dir.GetName()
    tfdir = dir.GetDirectory("transfer"); tfdir.cd()
    covers_hs = tfdir.Get("WJets")
    syslist = []
    for variation in variations:
        covers_up = tfdir.Get("WJets_%sUp" % variation)
        covers_dn = tfdir.Get("WJets_%sDown" % variation)
        if not validShape(covers_up,covers_dn): continue
        covers_sh = getFractionalShift(covers_hs,covers_up,covers_dn)
        var = RooRealVar("WJets_%s_%s" % (dir.GetName(),variation),"",0.,-5.,-5.)
        syslist.append( {'var':var,'histo':covers_sh} )
    ws.makeConnectedBinList("WJets_%s" % dir.GetName(),covers_hs,syslist,wbinlist)            

def getLCR(dir,rfile,ws,wbinlist):
    print 'Processing %s' % dir.GetName()
    dir.cd()

    variations = [ key.GetName().replace('ZJets_','').replace('Up','')
                   for key in dir.GetListOfKeys()
                   if 'ZJets' in key.GetName() and 'Up' in key.GetName() ]
    
    data_obs = dir.Get('data_obs'); data_obs.SetDirectory(0)
    ws.addTemplate('data_obs_%s' % dir.GetName(),data_obs)

    getLTransfer(dir,ws,variations,wbinlist)

    addMC(dir,ws,variations)

def createWorkspace(input):
    ws = Workspace('w','w')

    outfname = 'workspace.root'
    output = TFile(outfname,'recreate')
    var = RooRealVar('chnemptfrac','Ch + Nem P^{123}_{T} Fraction',0,1.1)
    ws.setVar(var)

    sysfile = TFile(input)

    #-----Signal Region-----#
    dir_sr = sysfile.GetDirectory('sr')
    zbinlist,wbinlist = getSignalRegion(dir_sr,sysfile,ws,signal=r"Mx\d*_Mv\d*$")

    #-----Double Muon-----#
    dir_mm = sysfile.GetDirectory('mm')
    getLLCR(dir_mm,sysfile,ws,zbinlist)
    
    #-----Double Electron-----#
    dir_mm = sysfile.GetDirectory('ee')
    getLLCR(dir_mm,sysfile,ws,zbinlist)

    #-----Single Muon-----#
    dir_m = sysfile.GetDirectory('m')
    getLCR(dir_m,sysfile,ws,wbinlist)

    #-----Single Electron-----#
    dir_e = sysfile.GetDirectory('e')
    getLCR(dir_e,sysfile,ws,wbinlist)

    output.cd()
    ws.Write()

if __name__ == "__main__":
    fbase = "ChNemPtFrac_2016.sys.root"
    cmssw_base = getenv("CMSSW_BASE")
    fname = "%s/src/HiggsAnalysis/CombinedLimit/ZprimeLimits/Systematics/2016/%s" % (cmssw_base,fbase)
    createWorkspace(fname)
