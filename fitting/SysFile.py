from ROOT import *

gSystem.Load("libHiggsAnalysisCombinedLimit.so")

dirmap = {"sr":"signal","ze":"Zee","zm":"Zmm","we":"Wen","wm":"Wmn","ga":"gjets"}
procmap = {"data":"data_obs","zjets":"ZJets","wjets":"WJets","zll":"DYJets","gjets":"GJets","top":"TTJets","diboson":"DiBoson","qcd":"QCD","axial":"axial","ggh":"ggh","vbf":"vbf","wh":"wh","zh":"zh","zprime":"zprime"}

yearlist = ["2016","2017","2018"]
lumimap = {"2016":35900,"2017":41486,"2018":59699}
catypes = ["monojet","monov","zprime"]
varmap = {
    "monojet":RooRealVar("recoil","recoil",250,1400),
    "zprime":RooRealVar("ChNemPtFrac","ChNemPtFrac",0.,1.0),
    # "zprime":RooRealVar("recoil","recoil",250,1400),
}

class SysRegion(TDirectoryFile):
    def __init__(self,region,syscat):
        TDirectoryFile.__init__(self,region,region+"_"+syscat.year)
        self.cat = syscat.cat
        self.year = syscat.year
        self.lumi = lumimap[self.year]
        for key in syscat.tdir.GetListOfKeys():
            if "zprime" in key.GetName():
               #r,p = "signal","axial"
               r,p = "signal",key.GetName().replace("signal_","")
            else :
               r,p = key.GetName().split("_")
            if dirmap[region] != r: continue
            if p == "sumofbkg": continue
            if "zprime" in p :  procname = p
            else :             procname = procmap[p]
            process = syscat.tdir.Get(key.GetName()).Clone(procname)
            self.Add(process)
class SysCat:
    def __init__(self,tdir):
        self.tdir = tdir
        self.cat = next( cat for cat in catypes if cat in self.tdir.GetName() )
        self.year = next( year for year in yearlist if year in self.tdir.GetName() )
        self.lumi = lumimap[self.year]
        self.var = varmap[self.cat]
        self.varlist = RooArgList(self.var)
    def GetRegion(self,region):
        self.sysregion = SysRegion(region,self)
        return self.sysregion
    def GetName(self): return "%s_%s.sys.root" % (self.var.GetTitle(),self.year)
    def getSignalList(self): 
            signal_mass_map =  {
                               #"Mchi":"Mphi"
                '10': ['10000', '100', '50', '15', '10'],
                '500': ['10000', '10', '995', '500'],
                '1000': ['10', '1000'],
                '50': ['10', '50', '10000', '300', '200', '95'],
                '150': ['1000', '200', '295', '500', '10000', '10'],
                '1': ['10', '50', '20', '200', '100', '10000', '1000']}
            return signal_mass_map


class SysFile(TFile):
    def __init__(self,*args,**kwargs):
        TFile.__init__(self,*args,**kwargs)
        self.categories = { category.GetName():SysCat(self.GetDirectory(category.GetName())) for category in self.GetListOfKeys() if self.GetDirectory(category.GetName()) }
        if not any(self.categories): self.categories = { self.GetName():SysCat(self) }
if __name__ == "__main__":
    import sys
    sysfile = SysFile(sys.argv[1])
    
    syscat = sysfile.categories["category_monojet_2017"]
    sysregion = syscat.GetRegion("sr")
    sysregion.Print()
