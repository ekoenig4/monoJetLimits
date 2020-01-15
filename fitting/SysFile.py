from ROOT import TFile,RooRealVar,gDirectory
import re

class SysFile(TFile):
    def __init__(self,fname):
        TFile.__init__(self,fname)
        self.year = int(self.Get('year').Integral())
        self.lumi = int(self.Get('lumi').Integral())
        self.variable = self.Get('variable')
    def getRooRealVar(self):
        return RooRealVar(self.variable.GetTitle(),self.variable.GetXaxis().GetTitle(),self.variable.GetXaxis().GetXmin(),self.variable.GetXaxis().GetXmax())
    def getMxlist(self):
        self.cd('sr')
        regexp = re.compile(r'Mx\d+_Mv\d+$')
        mxlist = {}
        def valid_signal(hs):
            # some signal has negative events, ignore them
            for ibin in range(1,len(hs)):
                if hs[ibin] < 0: return False
            return True
        for sample in gDirectory.GetListOfKeys():
            if regexp.search(sample.GetName()):
                if not valid_signal(gDirectory.Get(sample.GetName())): continue
                mx = sample.GetName().split('_')[0].replace('Mx','')
                mv = sample.GetName().split('_')[1].replace('Mv','')
                if mx not in mxlist: mxlist[mx] = []
                mxlist[mx].append(mv)
        return mxlist
if __name__ == "__main__":
    sysfile = SysFile('Systematics/2016/ChNemPtFrac+0.5_2016.sys.root')
