
def checkShape(shapeHist, name):
    negativeBins = False
    zeroBins = False
    for iBin in range(shapeHist.GetNbinsX()):
        b = shapeHist.GetBinContent(iBin + 1)
        if b < 0.:
            negativeBins = True
            shapeHist.SetBinContent(iBin + 1, 0.)
            shapeHist.SetBinError(iBin + 1, -b)
        elif b == 0.:
            zeroBins = True
    if negativeBins:
        # TODO: print if -vv or something
        print "Info: Negative bin content removed in shape histogram %s" % (name, )
    if zeroBins:
        # print "Info: Zero bin content found in shape histogram %s" % shapeHist.GetName()
        pass
    if shapeHist.Integral() == 0.:
        print "Warning: Integral zero in shape histogram %s" % (name, )
    if shapeHist.GetBinContent(0) != 0.:
        print "Info: zeroing underflow bin in shape histogram %s" % (name, )
        shapeHist.SetBinContent(0, 0.)
    if shapeHist.GetBinContent(shapeHist.GetNbinsX()+1) != 0.:
        print "Info: zeroing overflow bin in shape histogram %s" % (name, )
        shapeHist.SetBinContent(shapeHist.GetNbinsX()+1, 0.)

def binName(hist, iBin):
    return "bin%0.3fto%0.3f" % (hist.GetXaxis().GetBinLowEdge(iBin + 1), hist.GetXaxis().GetBinUpEdge(iBin + 1))
