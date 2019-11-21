from ROOT import *

def DataStyle(data):
    data.SetMarkerStyle(20)
    data.SetMarkerSize(1.7)
def BkgStyle(bkg):
    bkg.SetFillColor(kGray)
    bkg.SetLineColor(kGray)
def SignalStyle(signal):
    signal.SetLineWidth(2)
    signal.SetLineColor(kCyan)

def plotPrefit(tfile):
    prefit = tfile.GetDirectory('shapes_prefit')
    prefit.cd()

    prefit.ls()

    data = prefit.Get('total_data');      DataStyle(data)
    bkg = prefit.Get('total_background'); BkgStyle(bkg)
    signal = prefit.Get('total_signal');  SignalStyle(signal)

    data.Draw('AP')
    data.SetMinimum(0.1)
    bkg.Draw('hist same')
    signal.Draw('hist same')
    gPad.SetLogy()
    raw_input()

if __name__ == "__main__":
    fname = "Limits/ChNemPtFrac_2016.sys/verify/fitDiagnostics.root"
    tfile = TFile.Open(fname)

    plotPrefit(tfile)
    
