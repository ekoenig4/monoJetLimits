from ROOT import *

gSystem.Load("libHiggsAnalysisCombinedLimit.so")

class Workspace:
    def __init__(self,name,title):
        self.ws = RooWorkspace(name,title)
        self.var = None
        self.varlist = RooArgList()
        self.store = []
        
    def setVar(self,var):
        self.var = var
        self.varlist.add(var)
        
    def addTemplate(self,procname,hist):
        rhist = RooDataHist(procname,'',self.varlist,hist)
        getattr(self.ws,'import')(rhist)
        
    def makeBinList(self,procname,hist,setConst=False):
        binlist = RooArgList()
        store = []
        for i in range(1,hist.GetNbinsX() + 1):
            binv = hist[i]
            binss = '%s_bin%i' % (procname,i)
            if not setConst: binvar = RooRealVar(binss,'',binv,0.,1.1)
            else:            binvar = RooRealVar(binss,'',binv)
            store.append(binvar)
            self.binlist.add(binvar)
        #####
        normss = '%s_norm' % procname
        phist = RooParametricHist(procname,'',self.var,self.binlist,hist)
        norm = RooAddition(normss,'',self.binlist)

        getattr(self.ws,'import')(phist)
        getattr(self.ws,'import')(norm,RooFit.RecycleConflictNodes())
        return binlist
    def makeConnectedBinList(procname,rhist,syst,srbinlist,crbinlist=None):
        if crbinlist == None: crbinlist = RooArgList()
        store = []
        for i in range(1,rhist.GetNbinsX() + 1):
            rbinv = rhist[i]
            rerrbinv = rhist.GetBinError(i)
            rbinss= 'r_%s_bin%i' % (procname,i)
            rbinvar = RooRealVar(rbinss,'',rbinv)

            rerrbinss = '%s_bin%i_Runc' % (procname,i)
            rerrbinvar = RooRealVar(rerrbinss,'',0.,-5.,5.)

            binss = '%s_bin%i' % (procname,i)
            fobinlist = RooArgList()
            fobinlist.add(srbinlist[i-1])
            fobinlist.add(rbinvar)
            fobinlist.add(rerrbinvar)
            store.append( (rbinvar,rerrbinvar) )

            formss = '@0/(@1*TMath::Power(1+%f,@2)' % rerrbinv/rbinv
            for j,sys in enumerate(syst):
                if sys['var'] == None:
                    systbinss = '%s_%s_bin%i' % (procname,sys['histo'].GetName(),i)
                    systbinvar = RooRealVar(systbinss,'',0,-5.,5.)
                    sys['var'] = systbinvar
                fobinlist.add(sys['var'])
                store.add(sys['var'])
                forms += '*(TMath::Power(1+%f,@%i))' % (sys['histo'][i],j+3)
            forms += ')'
            binvar = RooFormulaVar(binss,'',formss,RooArgList(fobinlist))
            crbinlist.add(binvar)
            store.add(binvar)
        normss = '%s_norm' % procname
        phist = RooParametricHist(procname,'',self.var,crbinlist,rhist)
        norm = RooAddition(normss,'',crbinlist)
        getattr(self.ws,'import')(phist,RooFit.RecycleConflictNodes())
        getattr(self.ws,'import')(norm,RooFit.RecycleConflictNodes())
        
    def Write(self): self.ws.Write()
        
#####
if __name__ == "__main__":
    ws = Workspace('w','w')
    var = RooRealVar('var','var',0,1.1)
    ws.setVar(var)

    rfile = TFile.Open("ChNemPtFrac_2016.sys.root")
    dir_sr = rfile.GetDirectory('sr'); rfile.cd('sr')
    data_obs = dir_sr.Get('data_obs')

    ws.addTemplate('data_obs_SR',data_obs)

    ws.makeBinList('data_obs_SR',data_obs)

    output = TFile("workspace.root","recreate")
    ws.Write()
