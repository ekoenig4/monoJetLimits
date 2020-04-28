from ROOT import *
from sys import argv
import re

gROOT.SetBatch(1)
gStyle.SetOptStat(0)

var = 'recoil'
var = 'ChNemPtFrac'
# var = 'met_monojet_2018'

store = []

def iterset(rooset):
    iter = rooset.createIterator()
    object = iter.Next()
    while object:
        yield object
        object = iter.Next()
def selectRooParametricHist(pdflist):
    pdfset = RooArgSet()
    pdfiter = pdflist.createIterator()
    for _ in range(pdflist.getSize()):
        pdf = pdfiter.Next()
        if pdf.ClassName() == "RooParametricHist":
            pdfset.add(pdf)
    return pdfset
def plotVar(pdf,var,nuisance):
    if var == nuisance: return
    if nuisance.isConstant(): return
    if nuisance.getMax() > 10: return
    if 'bin' in nuisance.GetName() and 'bin0' not in nuisance.GetName(): return

    if 'bin' not in nuisance.GetName():
        name = nuisance.GetName()
        nuisances = [nuisance]
    else:
        name = nuisance.GetName().replace("_bin0","")
        wildcard = re.findall('bin\d+',nuisance.GetName())[0]
        wildcard = nuisance.GetName().replace(wildcard,'bin\d+')
        nuisances = [ nuisance for nuisance in iterset(pdf.getVariables())
                      if re.match(wildcard,nuisance.GetName())]
        # nuisances.sort(key=lambda r:r.GetName())
    for nuisance in nuisances:
        nuisance.setVal(0)
        nuisance.Print()
    
    nominal = pdf.createHistogram(name,var)
    evalNo = pdf.getValV()

    for nuisance in nuisances:
        nuisance.setVal(1)
    shiftUp = pdf.createHistogram(name+"shiftUp",var)
    evalUp = (pdf.getValV()-evalNo)/evalNo
    
    for nuisance in nuisances:
        nuisance.setVal(-1)
    shiftDn = pdf.createHistogram(name+"shiftDn",var)
    evalDn = (pdf.getValV()-evalNo)/evalNo

    print "--Integral: %f * (%f/%f)" % (evalNo,evalUp,evalDn)
    print
    shiftUp.Divide(nominal)
    shiftDn.Divide(nominal)
    nominal.Divide(nominal)

    
    shiftUp.SetLineColor(kRed)
    shiftDn.SetLineColor(kBlue)
    nominal.SetLineColor(kBlack)
    # nominal.SetFillColor(kGray)

    binlist = list(shiftUp)[1:-1] + list(shiftDn)[1:-1]
    ymin = min(binlist)
    ymax = max(binlist)
    diff = abs(ymax - ymin)


    canvas = TCanvas(pdf.GetName()+"_"+name,"%s %s"%(pdf.GetName(),name))
    canvas.SetLeftMargin(0.15)
    nominal.Draw("hist")
    shiftUp.Draw("histsame")
    shiftDn.Draw("histsame")
    nominal.GetYaxis().SetTitle(name)
    nominal.SetTitle(canvas.GetTitle())
    shiftUp.SetTitle(canvas.GetTitle())
    shiftDn.SetTitle(canvas.GetTitle())
    nominal.GetYaxis().SetRangeUser(ymin - 0.1*diff,ymax + 0.1*diff)
    store.append(canvas)
    canvas.Write()
    for nuisance in nuisances: nuisance.setVal(0.)
def plotPDF(pdf,var,output):
    pdf.Print()
    output.cd()
    cwd = output.mkdir(pdf.GetName())
    cwd.cd()
    pdf.createHistogram(pdf.GetName(),var).Write()
    nuisances = pdf.getVariables()
    for nuisance in iterset(nuisances): plotVar(pdf,var,nuisance)
if __name__ == "__main__":
    tfile = TFile(argv[1])
    ws = tfile.Get("w")
    var = ws.var(var)
    output = TFile(argv[2],"recreate")
    
    bkg_pdfs = ws.allPdfs().selectByName("shapeBkg*")
    bkg_pdfs = selectRooParametricHist(bkg_pdfs)
    for pdf in iterset(bkg_pdfs): plotPDF(pdf,var,output)

    sig_pdfs = ws.allPdfs().selectByName("shapeSig*")
    for pdf in iterset(sig_pdfs): plotPDF(pdf,var,output)
