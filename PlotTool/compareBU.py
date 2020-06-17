import sys
from ROOT import *
from PlotTool import *
from array import array
from argparse import ArgumentParser

parser = ArgumentParser()
parser.add_argument("-bu",help="BU File (numerator)",type=TFile)
parser.add_argument("-uw",help="UW File (denomenator)",type=TFile)
parser.add_argument("-mit",help="MIT File (numerator)",type=TFile,default=None)

gROOT.SetBatch(1)

outdir_base = "/afs/hep.wisc.edu/home/ekoenig4/public_html/MonoJet/"

def compareOutput(tfile_bu,tfile_uw,tfile_mit):
    def compareProcess(tcat_bu,tcat_uw,tcat_mit,hsname):
        print hsname
        hs_bu = tcat_bu.Get(hsname)
        hs_uw = tcat_uw.Get(hsname)

        if tcat_mit: hs_mit = tcat_mit.Get(hsname)

        # hs_bu.Scale(1,"width")
        # hs_uw.Scale(1,"width")
        
        hs_bu.SetTitle( hs_uw.GetTitle() )

        hs_bu.SetMarkerStyle(20)
        hs_bu.SetMarkerColor(kBlack)
        hs_bu.SetLineColor(kBlack)
        
        hs_uw.SetLineColor(kRed)
        hs_uw.SetLineWidth(2)

        if tcat_mit:
            hs_mit.SetLineColor(kBlue)
            hs_mit.SetLineWidth(2)

        c = TCanvas(hsname,hsname,800,800)
        c.SetLogy()
        gStyle.SetOptStat(0)
        gStyle.SetLegendBorderSize(0)
        c.SetTicks(0,1)

        ratio = TRatioPlot(hs_bu,hs_uw)
        ratio.SetH1DrawOpt("pex0")
        ratio.SetH2DrawOpt("histsame")
        ratio.SetGraphDrawOpt("p")
        ratio.Draw()
        hi = ratio.GetUpperRefObject()
        hi.GetYaxis().SetTitle("Events")

        upad = ratio.GetUpperPad()
        upad.cd()

        
        leg = getLegend(xmin=0.5,xmax=0.7)
        leg.AddEntry(hs_bu,"%s BU" % hsname,"pl")
        leg.AddEntry(hs_uw,"%s UW" % hsname,"fl")
        
        if tcat_mit:
            hs_mit.Draw("histsame")
            leg.AddEntry(hs_mit,"%s MIT"%hsname,"fl")
        leg.Draw()

        lo = ratio.GetLowerRefGraph()

        if lo.GetN() == 0:
            temp = hs_bu.Clone(); temp.Divide(hs_uw)
            for ibin in range(temp.GetNbinsX()):
                x = temp.GetXaxis().GetBinCenter(ibin+1)
                ex = temp.GetXaxis().GetBinWidth(ibin+1)
                y = temp.GetBinContent(ibin+1)
                ey = temp.GetBinError(ibin+1)
                lo.SetPoint(ibin,x,y)
                lo.SetPointError(ibin,ex,ex,ey,ey)
            lo.SetHistogram(temp)
        
        lo.GetYaxis().SetTitle("BU/UW")
        # lo.GetYaxis().SetRangeUser(0.45,1.55)
        lo.GetYaxis().SetRangeUser(0.89,1.11)
        ratio.SetGridlines(array('d',[1.05,1,0.95]),3)

        lo.SetMarkerStyle(20)
        lo.SetMarkerSize(1)
        lo.SetMarkerColor(kBlack)
        lo.SetLineColor(kBlack)
        lo.SetLineWidth(1)

        if tcat_mit:
            lpad = ratio.GetLowerPad()
            lpad.cd()
            lo.GetYaxis().SetTitle("(MIT,BU)/UW")
            mit_ratio = hs_mit.Clone()
            mit_ratio.Divide(hs_uw)
            mit_graph = TGraphAsymmErrors(mit_ratio)
            mit_graph.SetMarkerStyle(20)
            mit_graph.SetMarkerSize(1)
            mit_graph.SetMarkerColor(kBlue)
            mit_graph.SetLineWidth(1)
            mit_graph.Draw("psame")

        output = "%s/BU_Comparison/20200617_sync/bu_compare/%s/" % (outdir_base,tcat_bu.GetName())
        if not os.path.isdir(output): os.makedirs(output)
        c.SaveAs("%s/%s.png"%(output,hsname))
    def compareCategory(cat):
        print cat
        tcat_bu = tfile_bu.GetDirectory(cat)
        tcat_uw = tfile_uw.GetDirectory(cat)
        tcat_mit = None
        if tfile_mit: tcat_mit = tfile_mit.GetDirectory(cat)
        
        keylist_bu =[ key.GetName() for key in tcat_bu.GetListOfKeys()]
        keylist_uw =[ key.GetName() for key in tcat_uw.GetListOfKeys()]
        if tfile_mit: keylist_mit = [ key.GetName() for key in tcat_mit.GetListOfKeys() ]
        for key in keylist_bu:
            if key in keylist_uw:
                if tfile_mit and key not in keylist_mit: continue 
                compareProcess(tcat_bu,tcat_uw,tcat_mit,key)
    keylist_bu =[ key.GetName() for key in tfile_bu.GetListOfKeys()]
    keylist_uw =[ key.GetName() for key in tfile_uw.GetListOfKeys()]
    if tfile_mit: keylist_mit = [ key.GetName() for key in tfile_mit.GetListOfKeys() ]
    for key in keylist_bu:
        if key in keylist_uw:
            if tfile_mit and key not in keylist_mit: continue 
            compareCategory(key)

args = parser.parse_args()
compareOutput(args.bu,args.uw,args.mit)
    
