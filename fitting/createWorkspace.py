#!/usr/bin/env python
from ROOT import *
from os import getenv
from Workspace import Workspace
import re
import json
from SysFile import SysFile

gSystem.Load("libHiggsAnalysisCombinedLimit.so")

mclist = ['ZJets','WJets','DYJets','TTJets','DiBoson','GJets','QCD']

zw_variations = ["QCD_Scale","QCD_Shape","QCD_Proc","NNLO_EWK","NNLO_Miss","NNLO_Sud","QCD_EWK_Mix"]
cs_variations = []

options = {
    'doStats':True,
    'doTrans':True,
}

def validHisto(hs,total=0,threshold=0.2):
    return hs.Integral() > threshold*total

def validShape(up,dn):
    return any( up[ibin] != dn[ibin] for ibin in range(1,up.GetNbinsX()+1) ) and validHisto(up) and validHisto(dn)

def getVariations(dir):
    variations = [ key.GetName().replace('ZJets_','').replace('Up','')
                   for key in dir.GetListOfKeys()
                   if 'ZJets' in key.GetName() and 'Up' in key.GetName() ]
    return variations

def addStat(dir,ws,hs,name=None):
    if not options['doStats']: return
    if name == None: name = hs.GetName()
    for ibin in range(1,hs.GetNbinsX()+1):
        up = hs.Clone("%s_%s_histBinUp" % (hs.GetName(),dir.GetTitle()))
        dn = hs.Clone("%s_%s_histBinDown" % (hs.GetName(),dir.GetTitle()))
        up[ibin] = up[ibin] + up.GetBinError(ibin)
        dn[ibin] = max( 0.01*dn[ibin],dn[ibin] - dn.GetBinError(ibin))
        if not validShape(up,dn) and name != 'signal': continue

        variation = '%s_%s_bin%i_stat' % (name,dir.GetTitle(),ibin)
        ws.addTemplate("%s_%s_%sUp" % (hs.GetName(),dir.GetTitle(),variation),up)
        ws.addTemplate("%s_%s_%sDown" % (hs.GetName(),dir.GetTitle(),variation),dn)

def addMC(dir,ws,variations):
    print 'Processing %s MC' % dir.GetTitle()
    total_bkg = dir.Get('SumOfBkg').Integral()
    for mc in mclist:
        print 'Adding %s Process' % mc
        mc_hs = dir.Get(mc)
        if not validHisto(mc_hs): continue
        ws.addTemplate("%s_%s" % (mc,dir.GetTitle()),dir.Get(mc))
        for variation in variations:
            mc_up = dir.Get("%s_%sUp" % (mc,variation))
            mc_dn = dir.Get("%s_%sDown" % (mc,variation))
            if not validShape(mc_up,mc_dn): continue
            ws.addTemplate("%s_%s_%sUp" % (mc,dir.GetTitle(),variation),mc_up)
            ws.addTemplate("%s_%s_%sDown" % (mc,dir.GetTitle(),variation),mc_dn)
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

def ZWLink(dir,ws,connect):
    if not options['doTrans']: return [],[]
    print 'Processing %s Transfer Factors' % dir.GetTitle()
    zjet = dir.Get("ZJets")
    wjet = dir.Get("WJets")
    zbinlist = RooArgList()
    ws.makeBinList("ZJets_%s" % dir.GetTitle(),zjet,zbinlist)
    zwdir = dir.GetDirectory("transfer"); zwdir.cd()
    zoverw_hs = zwdir.Get("wsr_to_zsr")
    syslist = []
    for variation in zw_variations:
        if variation == 'JES': continue
        for process in ('wsr','zsr'):
            zoverw_up = zwdir.Get("wsr_to_zsr_%s_%sUp" % (variation,process))
            zoverw_dn = zwdir.Get("wsr_to_zsr_%s_%sDown" % (variation,process))
            if not validShape(zoverw_up,zoverw_dn): continue
            zoverw_sh = getFractionalShift(zoverw_hs,zoverw_up,zoverw_dn)
            var = RooRealVar("ZoverW_%s_%s_%s" % (dir.GetTitle(),process,variation),"",0.,-10.,10.)
            syslist.append( {'var':var,'histo':zoverw_sh} )
    wbinlist = RooArgList()
    if connect: ws.makeConnectedBinList("ZoverW_%s" % dir.GetTitle(),zoverw_hs,syslist,zbinlist,wbinlist)
    else:       ws.makeBinList("ZoverW_%s" % dir.GetTitle(),wjet,wbinlist)
    return zbinlist,wbinlist

def addSignal(dir,ws,variations,signals,isScaled):
    print 'Processing Signal'
    if type(signals) != list: signals = [signals]
    with open('signal_scaling.json') as f: scaling = json.load(f)
    def valid_signal(hs):
        # some signal has negative events, ignore them
        for ibin in range(1,len(hs)):
            if hs[ibin] < 0: return False
        return True
    for signal in signals:
        signal_hs = dir.Get(signal)
        signal_multi = 1
        signal_yield = signal_hs.Integral()
        if not valid_signal(signal_hs): print '%s has negative bins' % signal; continue
        if isScaled:
            signal_multi = scaling[signal] # Normalize so that combine limits are close to 1
            signal_hs.Scale(signal_multi)
        ws.addTemplate('%s_%s' % (signal,dir.GetTitle()),signal_hs)
        for variation in variations:
            signal_up = dir.Get("%s_%sUp"   % (signal,variation)); signal_up.Scale(signal_multi)
            signal_dn = dir.Get("%s_%sDown" % (signal,variation)); signal_dn.Scale(signal_multi)
            if not validShape(signal_up,signal_dn): continue
            ws.addTemplate("%s_%s_%sUp"   % (signal,dir.GetTitle(),variation),signal_up)
            ws.addTemplate("%s_%s_%sDown" % (signal,dir.GetTitle(),variation),signal_dn)
        addStat(dir,ws,signal_hs,name='signal')

def getSignalRegion(dir,sysfile,ws,signal,isScaled):
    print 'Processing sr'
    dir.cd()

    variations = getVariations(dir)
    
    data_obs = dir.Get('data_obs'); data_obs.SetDirectory(0)
    ws.addTemplate('data_obs_%s' % dir.GetTitle(),data_obs)

    nbins = data_obs.GetNbinsX()

    signal_scale = {}
    if signal != None:
        signals = [ key.GetName() for key in dir.GetListOfKeys() if re.search(signal,key.GetName()) ]
        addSignal(dir,ws,variations,signals,isScaled)
        

    zbinlist,wbinlist = ZWLink(dir,ws,True)

    addMC(dir,ws,variations)
    return zbinlist,wbinlist

def getLLTransfer(dir,ws,zbinlist):
    if not options['doTrans']: return
    print 'Processing %s Transfer Factors' % dir.GetTitle()
    tfdir = dir.GetDirectory("transfer"); tfdir.cd()
    soverc_hs = tfdir.Get("%s_to_sr" % dir.GetName())
    syslist = []
    # for variation in cs_variations:
    #     for process in 
    #     soverc_up = tfdir.Get("ZJets_%sUp" % variation)
    #     soverc_dn = tfdir.Get("ZJets_%sDown" % variation)
    #     if not validShape(soverc_up,soverc_dn): continue
    #     soverc_sh = getFractionalShift(soverc_hs,soverc_up,soverc_dn)
    #     var = RooRealVar("SRoverCR_%s_%s" % (dir.GetTitle(),variation),"",0.,-10.,10.)
    #     syslist.append( {'var':var,'histo':soverc_sh} )
    ws.makeConnectedBinList("SRoverCR_%s" % dir.GetTitle(),soverc_hs,syslist,zbinlist)

def getLLCR(dir,sysfile,ws,zbinlist):
    print 'Processing %s' % dir.GetTitle()
    dir.cd()

    variations = getVariations(dir)
    
    data_obs = dir.Get('data_obs');
    ws.addTemplate('data_obs_%s' % dir.GetTitle(),data_obs)

    getLLTransfer(dir,ws,zbinlist)

    addMC(dir,ws,variations)

def getLTransfer(dir,ws,wbinlist):
    if not options['doTrans']: return
    print 'Processing %s Transfer Factors' % dir.GetTitle()
    tfdir = dir.GetDirectory("transfer"); tfdir.cd()
    soverc_hs = tfdir.Get("%s_to_sr" % dir.GetName())
    syslist = []
    # for variation in cs_variations:
    #     soverc_up = tfdir.Get("WJets_%sUp" % variation)
    #     soverc_dn = tfdir.Get("WJets_%sDown" % variation)
    #     if not validShape(soverc_up,soverc_dn): continue
    #     soverc_sh = getFractionalShift(soverc_hs,soverc_up,soverc_dn)
    #     var = RooRealVar("SRoverCR_%s_%s" % (dir.GetTitle(),variation),"",0.,-10.,10.)
    #     syslist.append( {'var':var,'histo':soverc_sh} )
    ws.makeConnectedBinList("SRoverCR_%s" % dir.GetTitle(),soverc_hs,syslist,wbinlist)            

def getLCR(dir,sysfile,ws,wbinlist):
    print 'Processing %s' % dir.GetTitle()
    dir.cd()

    variations = getVariations(dir)
    
    data_obs = dir.Get('data_obs'); data_obs.SetDirectory(0)
    ws.addTemplate('data_obs_%s' % dir.GetTitle(),data_obs)

    getLTransfer(dir,ws,wbinlist)

    addMC(dir,ws,variations)

def getGTransfer(dir,ws,zbinlist):
    if not options['doTrans']: return
    print 'Processing %s Transfer Factors' % dir.GetTitle()
    tfdir = dir.GetDirectory("transfer"); tfdir.cd()
    soverc_hs = tfdir.Get("ga_to_sr")
    syslist = []
    for variation in zw_variations:
        for process in ('ga','sr'):
            soverc_up = tfdir.Get("ga_to_sr_%s_%sUp" % (variation,process))
            soverc_dn = tfdir.Get("ga_to_sr_%s_%sDown" % (variation,process))
            if not validShape(soverc_up,soverc_dn): continue
            soverc_sh = getFractionalShift(soverc_hs,soverc_up,soverc_dn)
            var = RooRealVar("SRoverCR_%s_%s_%s" % (dir.GetTitle(),process,variation),"",0.,-10.,10.)
            syslist.append( {'var':var,'histo':soverc_sh} )
    ws.makeConnectedBinList("SRoverCR_%s" % dir.GetTitle(),soverc_hs,syslist,zbinlist)
    
def getGCR(dir,sysfile,ws,zbinlist):
    print 'Processing %s' % dir.GetTitle()
    dir.cd()

    variations = getVariations(dir)
    
    data_obs = dir.Get('data_obs');
    ws.addTemplate('data_obs_%s' % dir.GetTitle(),data_obs)

    getGTransfer(dir,ws,zbinlist)

    addMC(dir,ws,variations)
    

def WriteScaling(signal_scale,output='signal_scaling.json'):
    with open(output,"w") as f:
        json.dump(signal_scale,f)

def getMetadata(sysfile,output):
    metadata = ['lumi','year','variable']
    output.cd()
    for meta in metadata:
        hs_meta = sysfile.Get(meta)
        hs_meta.Write()
        
def createWorkspace(input,isScaled=False,outfname='workspace.root'):
    sysfile = input
    if type(sysfile) == str: sysfile = SysFile(sysfile)
    ws = Workspace('w','w')

    output = TFile(outfname,'recreate')
    var = sysfile.getRooRealVar()
    ws.setVar(var)

    #-----Signal Region-----#
    dir_sr = sysfile.GetDirectory('sr')
    dir_sr.SetTitle('sr_%s' % sysfile.year)
    zbinlist,wbinlist = getSignalRegion(dir_sr,sysfile,ws,r"Axial_Mchi\d+_Mphi\d+$",isScaled)

    #-----Double Muon-----#
    dir_zm = sysfile.GetDirectory('zm')
    dir_zm.SetTitle('zm_%s' % sysfile.year)
    getLLCR(dir_zm,sysfile,ws,zbinlist)
    
    #-----Double Electron-----#
    dir_ze = sysfile.GetDirectory('ze')
    dir_ze.SetTitle('ze_%s' % sysfile.year)
    getLLCR(dir_ze,sysfile,ws,zbinlist)
    
    #-----Single Muon-----#
    dir_wm = sysfile.GetDirectory('wm')
    dir_wm.SetTitle('wm_%s' % sysfile.year)
    getLCR(dir_wm,sysfile,ws,wbinlist)
    
    #-----Single Electron-----#
    dir_we = sysfile.GetDirectory('we')
    dir_we.SetTitle('we_%s' % sysfile.year)
    getLCR(dir_we,sysfile,ws,wbinlist)
    
    #-----Single Photon-----#
    dir_ga = sysfile.GetDirectory('ga')
    dir_ga.SetTitle('ga_%s' % sysfile.year)
    getGCR(dir_ga,sysfile,ws,zbinlist)
    
    #-----Meta Data-----#
    getMetadata(sysfile,output)

    output.cd()
    ws.Write()

if __name__ == "__main__":
    fbase = "ChNemPtFrac_2016.sys.root"
    cmssw_base = getenv("CMSSW_BASE")
    fname = "%s/src/HiggsAnalysis/CombinedLimit/ZprimeLimits/Systematics/2016/%s" % (cmssw_base,fbase)
    createWorkspace(fname)
    
