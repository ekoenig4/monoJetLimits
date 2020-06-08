import sys
from ROOT import *
from PlotTool import *

gROOT.SetBatch(1)

outdir_base = "/afs/hep.wisc.edu/home/ekoenig4/public_html/MonoJet/"

def compareOutput(fname1,fname2):
    tfile1 = TFile.Open(fname1)
    tfile2 = TFile.Open(fname2)

    def compareProcess(tcat1,tcat2,hsname):
        if hsname != "signal_zjets": return
        print hsname
        hs1 = tcat1.Get(hsname)
        hs2 = tcat2.Get(hsname)

        hs2.Scale(1,"width")
        hs1.SetTitle( hs2.GetTitle() )

        hs1.SetMarkerStyle(20)
        hs1.SetMarkerColor(kBlack)
        hs1.SetLineColor(kBlack)
        
        hs2.SetLineColor(kRed)
        hs2.SetLineWidth(2)

        c = TCanvas(hsname,hsname,800,800)
        c.SetLogy()
        gStyle.SetOptStat(0)
        gStyle.SetLegendBorderSize(0)
        c.SetTicks(0,1)

        ratio = TRatioPlot(hs1,hs2)
        ratio.SetH1DrawOpt("pex0")
        ratio.SetH2DrawOpt("histsame")
        ratio.SetGraphDrawOpt("p")
        ratio.Draw()
        hi = ratio.GetUpperRefObject()
        hi.GetYaxis().SetTitle("Events")

        upad = ratio.GetUpperPad()
        upad.cd()
        leg = getLegend(xmin=0.5,xmax=0.7)
        leg.AddEntry(hs1,"%s BU" % hsname,"pl")
        leg.AddEntry(hs2,"%s UW" % hsname,"fl")
        leg.Draw()

        lo = ratio.GetLowerRefGraph()

        if lo.GetN() == 0:
            temp = hs1.Clone(); temp.Divide(hs2)
            for ibin in range(temp.GetNbinsX()):
                x = temp.GetXaxis().GetBinCenter(ibin+1)
                ex = temp.GetXaxis().GetBinWidth(ibin+1)
                y = temp.GetBinContent(ibin+1)
                ey = temp.GetBinError(ibin+1)
                lo.SetPoint(ibin,x,y)
                lo.SetPointError(ibin,ex,ex,ey,ey)
            lo.SetHistogram(temp)
        
        lo.GetYaxis().SetTitle("BU/UW")
        lo.GetYaxis().SetRangeUser(0.45,1.55)

        lo.SetMarkerStyle(20)
        lo.SetMarkerSize(1)

        output = "%s/BU_Comparison/20200601_sync/%s/" % (outdir_base,tcat1.GetName())
        if not os.path.isdir(output): os.makedirs(output)
        c.SaveAs("%s/%s.png"%(output,hsname))
    def compareCategory(cat):
        print cat
        tcat1 = tfile1.GetDirectory(cat)
        tcat2 = tfile2.GetDirectory(cat)
        
        keylist1 =[ key.GetName() for key in tcat1.GetListOfKeys()]
        keylist2 =[ key.GetName() for key in tcat2.GetListOfKeys()]
        for key in keylist1:
            if key in keylist2:
                compareProcess(tcat1,tcat2,key)
    keylist1 =[ key.GetName() for key in tfile1.GetListOfKeys()]
    keylist2 =[ key.GetName() for key in tfile2.GetListOfKeys()]
    for key in keylist1:
        if key in keylist2:
            compareCategory(key)

compareOutput(sys.argv[1],sys.argv[2])
    
