from ROOT import *

gSystem.Load("libHiggsAnalysisCombinedLimit.so")

class SysFile(TFile):
    def __init__(self,*args,**kwargs):
        TFile.__init__(self,*args,**kwargs)
        self.lumi = self.Get("lumi").Integral()
        self.year = self.Get("year").Integral()
        self.variable = self.Get("variable")
        self.var = RooRealVar(self.variable.GetTitle(),self.variable.GetXaxis().GetTitle(),self.variable.GetXaxis().GetXmin(),self.variable.GetXaxis().GetXmax())
        self.varlist = RooArgList(self.var)
    def GetDirectory(self,*args,**kwargs):
        directory = TFile.GetDirectory(self,*args,**kwargs)
        directory.SetTitle('%s_%i' % (directory.GetName(),self.year))
        return directory
