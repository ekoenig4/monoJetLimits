from ROOT import TMath,TGraph,Double
import os
from central_signal import central_signal
import re
from array import array

def checkdir(dir):
    if not os.path.isdir(dir):
        print 'Making %s' % dir
        os.mkdir(dir)
def include_central(data):
    mx_pattern = re.compile('Mx\d+'); mv_pattern = re.compile('Mv\d+')
    
    mx_include = [ mx_pattern.findall(signal)[0].replace('Mx','') for signal in central_signal ]
    mv_include = [ mv_pattern.findall(signal)[0].replace('Mv','') for signal in central_signal ]
    
    for mx in data.keys():
        if str(mx) not in mx_include: data.pop(mx)
    for _,mvlist in data.items():
        rmlist = [ mv for mv in mvlist if not str(mv) in mv_include ]
        for rm in rmlist: mvlist.remove(rm)
def SigmaPull(norm,postfit):
    tmp = norm.Clone()
    nbins = tmp.GetNbinsX()
    avg = sum( postfit[ibin] for ibin in range(1,nbins+1) )/float(nbins)
    stdv = TMath.Sqrt( sum( (postfit[ibin] - avg)**2 for ibin in range(1,nbins+1) )/float(nbins-1) )
    for ibin in range(1,nbins+1):
        tmp[ibin] = (norm[ibin] - postfit[ibin])/stdv
    return tmp

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
