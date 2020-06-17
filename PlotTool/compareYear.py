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
    def compareProcess(tcat_17,tcat_18,hsname,label):
        print hsname
        hs_17 = tcat_17.Get(hsname)
        hs_18 = tcat_18.Get(hsname)

        hs_17.Scale(59699./41486.)

        # hs_17.Scale(1,"width")
        # hs_18.Scale(1,"width")
        
        hs_17.SetTitle( "%s %s"%(label.upper(),hsname) )

        hs_17.SetMarkerStyle(20)
        hs_17.SetMarkerColor(kBlack)
        hs_17.SetLineColor(kBlack)
        
        hs_18.SetLineColor(kRed)
        hs_18.SetLineWidth(2)

        c = TCanvas(hsname,hsname,800,800)
        c.SetLogy()
        gStyle.SetOptStat(0)
        gStyle.SetLegendBorderSize(0)
        c.SetTicks(0,1)

        ratio = TRatioPlot(hs_17,hs_18)
        ratio.SetH1DrawOpt("pex0")
        ratio.SetH2DrawOpt("histsame")
        ratio.SetGraphDrawOpt("p")
        ratio.Draw()
        hi = ratio.GetUpperRefObject()
        hi.GetYaxis().SetTitle("Events")

        upad = ratio.GetUpperPad()
        upad.cd()

        
        leg = getLegend(xmin=0.5,xmax=0.7)
        leg.AddEntry(hs_17,"%s 2017" % hsname,"pl")
        leg.AddEntry(hs_18,"%s 2018" % hsname,"fl")
        leg.Draw()

        lo = ratio.GetLowerRefGraph()

        if lo.GetN() == 0:
            temp = hs_17.Clone(); temp.Divide(hs_18)
            for ibin in range(temp.GetNbinsX()):
                x = temp.GetXaxis().GetBinCenter(ibin+1)
                ex = temp.GetXaxis().GetBinWidth(ibin+1)
                y = temp.GetBinContent(ibin+1)
                ey = temp.GetBinError(ibin+1)
                lo.SetPoint(ibin,x,y)
                lo.SetPointError(ibin,ex,ex,ey,ey)
            lo.SetHistogram(temp)
        
        lo.GetYaxis().SetTitle("2017/2018")
        # lo.GetYaxis().SetRangeUser(0.45,1.55)
        lo.GetYaxis().SetRangeUser(0.74,1.26)
        ratio.SetGridlines(array('d',[1.1,1,0.9]),3)

        lo.SetMarkerStyle(20)
        lo.SetMarkerSize(1)
        lo.SetMarkerColor(kBlack)
        lo.SetLineColor(kBlack)
        lo.SetLineWidth(1)

        output = "%s/BU_Comparison/20200617_sync/year_compare/%s/" % (outdir_base,label)
        if not os.path.isdir(output): os.makedirs(output)
        c.SaveAs("%s/%s.png"%(output,hsname))
    def compareCategory(tfile,cat,label):
        tcat_17 = tfile.GetDirectory(cat.format(year="2017"))
        tcat_18 = tfile.GetDirectory(cat.format(year="2018"))
        
        keylist_17 =[ key.GetName() for key in tcat_17.GetListOfKeys()]
        keylist_18 =[ key.GetName() for key in tcat_18.GetListOfKeys()]
        for key in keylist_17:
            if key in keylist_18:
                compareProcess(tcat_17,tcat_18,key,label)

    cat = "category_monojet_{year}"
    compareCategory(tfile_uw,cat,"uw")
    compareCategory(tfile_bu,cat,"bu")
    compareCategory(tfile_mit,cat,"mit")
    

args = parser.parse_args()
compareOutput(args.bu,args.uw,args.mit)
    
