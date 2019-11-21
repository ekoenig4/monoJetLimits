from ROOT import TH2D,TGraph

def Plot1D(data):
    mxlist = sorted(data.data.keys(),key=int)
    limits = {}
    for mx in mxlist:
        xlist = []; ylist = []
        for i,mv in enumerate( sorted(data.data[mx],key=float) ):
            x = float(mv); y = data.data[mx][mv]['exp0']
            xlist.append(x); ylist.append(y)
        xlist = array('d',xlist); ylist = array('d',ylist);
        limits[mx] = TGraph(len(xlist),xlist,ylist)
    return limits,mxlist
#####################################################################
def Plot2D(data):
    mxlist = sorted(data.data.keys(),key=int)
    mxbins = { mx:i+1 for i,mx in enumerate(mxlist) }
    mvlist = []
    for mx in mxlist:
        for mv in sorted(data.data[mx],key=float):
            if mv not in mvlist: mvlist.append(mv); mvlist.sort(key=float)
    mvbins = { mv:i+1 for i,mv in enumerate(mvlist) }
    xbins = len(mvlist); ybins = len(mxlist)
    limit = TH2D("Expected Limits","",xbins,0,xbins,ybins,0,ybins)
    for mx in mxlist:
        for mv in data[mx]:
            limit.SetBinContent(mvbins[mv],mxbins[mx],data[mx][mv]['exp0'])
    return limit,mxlist,mvlist
#######################################################################
