from ROOT import TH2D,TGraph
from array import *

def Plot1D(data,exclude=None):
    datalist = data.getDatalist(exclude)
    mxlist = sorted(datalist.keys(),key=int)
    limits = {}
    for mx in mxlist:
        xlist = []; ylist = []
        for i,mv in enumerate( sorted(datalist[mx],key=float) ):
            if not 'exp0' in data.data[mx][mv]:
                data.data[mx].pop(mv)
                datalist[mx].remove(mv)
                continue
            x = float(mv); y = data.data[mx][mv]['exp0']
            xlist.append(x); ylist.append(y)
        if not any(xlist) or not any(ylist):
            mxlist.remove(mx)
            datalist.pop(mx)
            data.data.pop(mx)
            continue
        xlist = array('d',xlist); ylist = array('d',ylist);
        limits[mx] = TGraph(len(xlist),xlist,ylist)
    return limits,mxlist
#####################################################################
def Plot2D(data,exclude=None):
    datalist = data.getDatalist(exclude)
    mxlist = sorted(datalist.keys(),key=int)
    mvlist = []
    for mx in mxlist:
        for mv in sorted(datalist[mx],key=float):
            if mv not in mvlist: mvlist.append(mv); mvlist.sort(key=float)
    xbins = len(mvlist); ybins = len(mxlist)
    limit = TH2D("Expected Limits",";m_{med} (GeV);m_{#chi} (GeV)",xbins,0,xbins,ybins,0,ybins)
    for mx in mxlist:
        for mv in mvlist:
            if mv not in data.data[mx]: lim = 0
            else:                       
                if not 'exp0' in data.data[mx][mv]:
                    data.data[mx].pop(mv)
                    datalist[mx].remove(mv)
                    continue
                lim = data.data[mx][mv]['exp0']
            limit.Fill(mv,mx,lim)
    return limit,mxlist,mvlist
#######################################################################
