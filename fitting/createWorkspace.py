#!/usr/bin/env python
from ROOT import *
from SysFile import *
import os
import re
import json

gSystem.Load("libHiggsAnalysisCombinedLimit.so")

def irange(lo,hi): return range(lo,hi+1)
def validHisto(hs,total=0,threshold=0.2): return hs.Integral() > threshold*total
def validShape(up,dn): return any( up[ibin] != dn[ibin] for ibin in range(1,up.GetNbinsX()+1) ) and validHisto(up) and validHisto(dn)

def getFractionalShift(norm,up,dn):
    sh = up.Clone( up.GetName().replace('Up','') ); sh.Reset()
    for ibin in irange(1,sh.GetNbinsX()):
        if norm[ibin] != 0:
            upshift = up[ibin]/norm[ibin] - 1.
            dnshift = dn[ibin]/norm[ibin] - 1.
            shiftEnvelope = max( abs(upshift),abs(dnshift) )
        else: shiftEnvelope = 0
        sh[ibin] = shiftEnvelope
    return sh

class BinList:
    def __init__(self,procname,sysdir,var,setConst=False):
        self.procname = procname
        self.sysdir = sysdir
        self.sysdir.cd()
        self.var = var
        self.bkg_obs = self.sysdir.Get(self.procname).Clone("%s_%s"%(self.procname,self.sysdir.GetTitle()))
        self.binstore = []
        self.binlist = RooArgList()
        for i in irange(1,self.bkg_obs.GetNbinsX()):
            bin_name = "%s_%s_bin%i" % (self.procname,self.sysdir.GetTitle(),i)
            bin_label = "%s Yield in %s, bin %i" % (self.procname,self.sysdir.GetTitle(),i)
            bin_yield = self.bkg_obs.GetBinContent(i)
            if setConst: nbin = RooRealVar(bin_name,bin_label,bin_yield)
            else:        nbin = RooRealVar(bin_name,bin_label,bin_yield,0,2000.0)
            self.binstore.append(nbin)
            self.binlist.add(nbin)
        self.p_bkg = RooParametricHist(self.bkg_obs.GetName(),"%s PDF in %s"%(self.procname,self.sysdir.GetTitle()),self.var,self.binlist,self.bkg_obs)
        self.p_bkg_norm = RooAddition("%s_norm"%self.bkg_obs.GetName(),"%s total events in %s"%(self.procname,self.sysdir.GetTitle()),self.binlist)
    def Export(self,ws):
        ws.Import(self.p_bkg)
        ws.Import(self.p_bkg_norm,RooFit.RecycleConflictNodes())
        
class ConnectedBinList:
    def __init__(self,procname,sysdir,var,tf_proc,tf_channel):
        self.tf_proc = tf_channel.bkgmap[ tf_proc[procname] ]
        self.tfname = tf_proc[id]
        self.procname = procname
        self.sysdir = sysdir
        self.sysdir.cd()
        self.var = var

        self.bkg_tf = self.sysdir.Get('transfer/%s'%self.tfname).Clone("%s_%s"%(self.procname,self.sysdir.GetTitle()))
        self.addSyst()
        self.binstore = []
        self.formulastore = []
        self.statstore = []
        self.binlist = RooArgList()
        for i in irange(1,self.bkg_tf.GetNbinsX()):
            bin_name = "%s_bin%i" % (self.bkg_tf.GetName(),i)
            bin_label = "%s TF Ratio, bin %i" % (self.bkg_tf.GetName(),i)
            bin_ratio = self.bkg_tf.GetBinContent(i)

            formula_binlist = RooArgList()
            tfbin = self.tf_proc.binlist[i-1]
            nbin = RooRealVar("r_"+bin_name,bin_label,bin_ratio)
            self.binstore.append(nbin)
            
            formula_binlist.add(tfbin)
            formula_binlist.add(nbin)
            num = "@0" # sr yield
            den = "@1" # sr/cr yield
            j = -1
            for j,syst in enumerate(self.systs.values()):
                formula_binlist.add( syst[RooRealVar] )
                den += '*(TMath::Power(1+%f,@%i))'%(syst[TH1F].GetBinContent(i),j+2)
            statvar = RooRealVar("%s_bin%i_Runc" % (self.bkg_tf.GetName(),i),"%s TF Stats, bin %i" % (self.bkg_tf.GetName(),i),0.,-10.,-10.)
            den += "*(TMath::Power(1+%f,@%i))"%(self.bkg_tf.GetBinError(i)/bin_ratio,j+3)
            self.statstore.append(statvar)
            formula_binlist.add(statvar)
            formula = "%s/(%s)"%(num,den)
            bin_formula = RooFormulaVar(bin_name,bin_label,formula,formula_binlist)
            self.formulastore.append(bin_formula)
            self.binlist.add(bin_formula)
        self.p_bkg = RooParametricHist(self.bkg_tf.GetName(),"%s PDF in %s"%(self.procname,self.sysdir.GetTitle()),self.var,self.binlist,self.bkg_tf)
        self.p_bkg_norm = RooAddition("%s_norm"%self.bkg_tf.GetName(),"%s total events in %s"%(self.procname,self.sysdir.GetTitle()),self.binlist)
    def addSyst(self,skip=["Stat","Total"]):
        self.systs = { syst.GetName().replace(self.tfname+'_',"").replace("Up",""):None
                       for syst in self.sysdir.GetDirectory("transfer").GetListOfKeys()
                       if self.tfname in syst.GetName() and 'Up' in syst.GetName() and
                       not any( ignore in syst.GetName() for ignore in skip ) }
        for syst in self.systs.keys():
            up = self.sysdir.Get("transfer/%s_%sUp"%(self.tfname,syst)).Clone("%s_%s_%sUp"%(self.tfname,self.sysdir.GetTitle(),syst))
            dn = self.sysdir.Get("transfer/%s_%sDown"%(self.tfname,syst)).Clone("%s_%s_%sDown"%(self.tfname,self.sysdir.GetTitle(),syst))
            if not validShape(up,dn): continue
            envelope = getFractionalShift(self.bkg_tf,up,dn)
            systvar = RooRealVar(envelope.GetName(),"%s TF Ratio"%envelope.GetName(),0.,-10.,-10.)
            self.systs[syst] = {RooRealVar:systvar,TH1F:envelope,'store':[]}
    def Export(self,ws):
        ws.Import(self.p_bkg)
        ws.Import(self.p_bkg_norm,RooFit.RecycleConflictNodes())
class Nuisance:
    def __init__(self,procname,obs,varlist):
        self.procname = procname
        self.varlist = varlist
        
        self.obs = obs
        self.hist = RooDataHist(self.obs.GetName(),"%s Observed"%self.obs.GetName(),self.varlist,self.obs)
    def Export(self,ws): ws.Import(self.hist)
class Template:
    def __init__(self,procname,sysdir,varlist):
        self.procname = procname
        self.sysdir = sysdir
        self.sysdir.cd()
        self.varlist = varlist

        self.obs = self.sysdir.Get(self.procname).Clone("%s_%s"%(self.procname,self.sysdir.GetTitle()))
        self.hist = RooDataHist(self.obs.GetName(),"%s Observed"%self.obs.GetName(),self.varlist,self.obs)

        if 'Up' in self.procname or 'Down' in self.procname: return
        
        self.nuisances = { nuisance.replace(self.procname+'_',"").replace("Up",""):None
                           for nuisance in self.sysdir.keylist
                           if re.match('^'+self.procname,nuisance) and 'Up' in nuisance }
        
        for nuisance in self.nuisances.keys():
            up = self.sysdir.Get("%s_%sUp"%(self.procname,nuisance)).Clone("%s_%s_%sUp"%(self.procname,self.sysdir.GetTitle(),nuisance))
            dn = self.sysdir.Get("%s_%sDown"%(self.procname,nuisance)).Clone("%s_%s_%sDown"%(self.procname,self.sysdir.GetTitle(),nuisance))
            if not validShape(up,dn): continue
            self.nuisances[nuisance] = {'up':Nuisance(up.GetName(),up,self.varlist),'dn':Nuisance(dn.GetName(),dn,self.varlist)}
    def Export(self,ws):
        ws.Import(self.hist)
        for nuisance in self.nuisances.values():
            if not nuisance: continue
            for variation in ('up','dn'): nuisance[variation].Export(ws)
class Channel:
    bkglist = ["ZJets","DYJets","WJets","GJets","QCD","DiBoson","TTJets"]
    majormap = {
        "sr":"ZJets" # Need to generate binlist for sr zjets so that it can be used in other connected bin lists
    }
    def __init__(self,sysfile,sysdir,signals=[],tf_proc={},tf_channel=None):
        if any(tf_proc) and tf_channel is None: tf_channel = self
        self.sysfile = sysfile
        self.sysdir = sysfile.GetDirectory(sysdir)
        self.sysdir.keylist = [ key.GetName() for key in self.sysdir.GetListOfKeys() ]
        self.sysdir.cd()

        self.data = Template('data_obs',self.sysdir,self.sysfile.varlist)
        self.bkgmap = {}
        for bkg in self.bkglist:
            if bkg in tf_proc:
                self.bkgmap[bkg] = ConnectedBinList(bkg,self.sysdir,self.sysfile.var,tf_proc,tf_channel)
            elif self.sysdir.GetName() in self.majormap and bkg == self.majormap[self.sysdir.GetName()]:
                self.bkgmap[bkg] = BinList(bkg,self.sysdir,self.sysfile.var)
            else:
                self.bkgmap[bkg] = Template(bkg,self.sysdir,self.sysfile.varlist)
        if not any(signals): return
        self.signals = list(signals)
        self.signalmap = { signal:Template(signal,self.sysdir,self.sysfile.varlist) for signal in signals }
    def Export(self,ws):
        self.data.Export(ws)
        for bkg in self.bkglist: self.bkgmap[bkg].Export(ws)
        if not hasattr(self,'signals'): return
        for signal in self.signals: self.signalmap[signal].Export(ws)
        
class Workspace(RooWorkspace):
    def __init__(self,*args,**kwargs):
        RooWorkspace.__init__(self,*args,**kwargs)
        self.Import = getattr(self,'import')
    def SignalRegion(self,sysfile,signals):
        sysfile.sr = Channel(sysfile,'sr',signals,tf_proc={"WJets":"ZJets",id:"wsr_to_zsr"})
        sysfile.sr.Export(self)
    def SingleEleCR(self,sysfile):
        sysfile.we = Channel(sysfile,'we',tf_proc={"WJets":"WJets",id:"we_to_sr"},tf_channel=sysfile.sr)
        sysfile.we.Export(self)
    def SingleMuCR(self,sysfile):
        sysfile.wm = Channel(sysfile,'wm',tf_proc={"WJets":"WJets",id:"wm_to_sr"},tf_channel=sysfile.sr)
        sysfile.wm.Export(self)
    def DoubleEleCR(self,sysfile):
        sysfile.ze = Channel(sysfile,'ze',tf_proc={"DYJets":"ZJets",id:"ze_to_sr"},tf_channel=sysfile.sr)
        sysfile.ze.Export(self)
    def DoubleMuCR(self,sysfile):
        sysfile.zm = Channel(sysfile,'zm',tf_proc={"DYJets":"ZJets",id:"zm_to_sr"},tf_channel=sysfile.sr)
        sysfile.zm.Export(self)
    def GammaCR(self,sysfile):
        sysfile.ga = Channel(sysfile,'ga',tf_proc={"GJets":"ZJets",id:"ga_to_sr"},tf_channel=sysfile.sr)
        sysfile.ga.Export(self)
if __name__ == "__main__":
    sysfile = SysFile("../Systematics/2017/recoil_2017.sys.root")
    output = TFile("workspace.root","recreate")
    ws = Workspace("w","w")

    signals = ['Axial_Mchi1_Mphi1000']
    ws.SignalRegion(sysfile,signals)
    ws.SingleEleCR(sysfile)
    ws.SingleMuCR(sysfile)
    ws.DoubleEleCR(sysfile)
    ws.DoubleMuCR(sysfile)
    ws.GammaCR(sysfile)

    output.cd()
    ws.Write()
    
