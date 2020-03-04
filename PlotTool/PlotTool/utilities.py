from ROOT import TMath,TGraph,Double,TH1
import os
from central_signal import central_signal
import re
from array import array

def checkdir(dir):
    if not os.path.isdir(dir):
        print 'Making %s' % dir
        os.mkdir(dir)
def include_central(data):
    mx_pattern = re.compile('Mchi\d+'); mv_pattern = re.compile('Mphi\d+')
    
    mx_include = [ mx_pattern.findall(signal)[0].replace('Mchi','') for signal in central_signal ]
    mv_include = [ ]
    for signal in central_signal:
        mv = mv_pattern.findall(signal)[0].replace('Mphi','')
        if mv == '10000': continue
        if not mv in mv_include: mv_include.append(mv)
        
    for mx in data.keys():
        if str(mx) not in mx_include: data.pop(mx)
    for _,mvlist in data.items():
        rmlist = [ mv for mv in mvlist if not str(mv) in mv_include ]
        for rm in rmlist: mvlist.remove(rm)
def SigmaPull(data,postfit,show=True):
    pull = data.Clone("pull")
    pull.Add(postfit,-1)
    TH1.StatOverflows(1)

    addedsqrt = 0
    mean = 0
    sigma = 0
    chi2 = 0
    for ibin in range(1,pull.GetNbinsX()+1):
        if postfit[ibin] <= 0: continue
        addedsqrt += (pull.GetBinContent(ibin)**2)/(postfit.GetBinError(ibin)**2)
        sigma = TMath.Sqrt(postfit.GetBinError(ibin)**2 + data.GetBinError(ibin)**2)
        pull.SetBinContent(ibin,pull.GetBinContent(ibin)/sigma)

        pull.SetBinError(ibin,0)
        mean += pull.GetBinContent(ibin)
        chi2 += pull.GetBinContent(ibin)**2

    if show:
        print "MEAN: ", mean/pull.GetNbinsX()
        print "CHI2: ", TMath.Sqrt(chi2)/pull.GetNbinsX()
        
        print "Added", TMath.Sqrt(addedsqrt), "divided: ", TMath.Sqrt(addedsqrt)/pull.GetNbinsX()
        print "Added2", addedsqrt, "divided: ", addedsqrt/pull.GetNbinsX()
    
    return pull
def makeHistogram(graph,template):
    hs = template.Clone();
    npoints = graph.GetN()
    for i in range(npoints):
        x,y=Double(0),Double(0)
        graph.GetPoint(i,x,y)
        xerr = graph.GetErrorX(i)
        yerr = graph.GetErrorY(i)
        hs.SetBinContent(i+1,y)
        hs.SetBinError(i+1,yerr)
    return hs;

def GetRatio(num,den):
    def TGraphHelper(num,den):
        npoints = num.GetN()
        xlist = []; ylist = []
        for i in range(npoints):
            x1,x2,y1,y2 = Double(),Double(),Double(),Double()
            num.GetPoint(i,x1,y1); den.GetPoint(i,x2,y2)
            xlist.append(x1)
            ylist.append(y1/y2)
        return TGraph(npoints,array('d',xlist),array('d',ylist))
    if type(num) == TGraph and type(den) == TGraph:
        return TGraphHelper(num,den)
