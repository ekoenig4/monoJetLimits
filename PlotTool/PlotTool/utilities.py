from ROOT import *

def SigmaPull(norm,prefit,postfit):
    tmp = norm.Clone()
    for ibin in range(1,tmp.GetNbinsX()+1):
        sign = int((postfit[ibin] - prefit[ibin])/abs(postfit[ibin] - prefit[ibin]))
        array = [ norm[ibin] - hs[ibin] for hs in (postfit,prefit) ]
        avg = sum( val for val in array )/len(array)
        stdv= TMath.Sqrt( sum( (val - avg)**2 for val in array ) /(len(array)-1) )
        tmp[ibin] = (norm[ibin]-postfit[ibin])/stdv
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
