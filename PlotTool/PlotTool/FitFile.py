from ROOT import TFile
from utilities import *

regionmap = {
    'we':{'mc':'WJets','leg':'W #rightarrow e#nu'},
    'wm':{'mc':'WJets','leg':'W #rightarrow #mu#nu'},
    'ze':{'mc':'DYJets','leg':'Z #rightarrow ee'},
    'zm':{'mc':'DYJets','leg':'Z #rightarrow #mu#mu'},
    'ga':{'mc':'GJets','leg':'#gamma + jets'}
}
class FitFile(TFile):
    def __init__(self,*args,**kwargs):
        TFile.__init__(self,*args,**kwargs)
        self.nuisances = self.Get('nuisances_prefit')
        self.region = None
    def getRegion(self,region):
        self.region = region
        self.prefit_hs = self.Get('shapes_prefit/%s/total_background' % (region))
        self.postfit_hs = self.Get('shapes_fit_b/%s/total_background' % (region))
        self.data_graph = self.Get('shapes_prefit/%s/data' % region)
        self.data_hs = makeHistogram(self.data_graph,self.prefit_hs)
    def getFitRatio(self):
        self.prefit_ratio = self.data_hs.Clone('prefit_ratio')
        self.prefit_ratio.Divide(self.prefit_hs)
        self.postfit_ratio = self.data_hs.Clone('postfit_ratio')
        self.postfit_ratio.Divide(self.postfit_hs)
    def getSigmaPull(self,show=True):
        self.sigma_pull = SigmaPull(self.data_hs,self.postfit_hs)
    def getOtherBkg(self,region,mclist = ['ZJets','WJets','DYJets','GJets','TTJets','QCD','EWK']):
        bkg = None
        tdir = self.Get('shapes_prefit/%s' % region)
        print [key.GetName() for key in tdir.GetListOfKeys() ]
        for mc in mclist:
            if regionmap[region]['mc'] in mc: continue
            tmp = tdir.Get('%s' % mc)
            if tmp == None: continue
            if bkg is None: bkg = tmp
            else:           bkg.Add(tmp)
        self.other_bkg = bkg
