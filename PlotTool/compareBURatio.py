import sys
sys.path.append("PlotTool")
from ROOT import *
from PlotTool import *
import config

parser.parse_args()

gROOT.SetBatch(1)

regionlist = [ "Wen","Wmn","Zee","Zmm","gjets" ]
processMap = {
    "signal": {
        "Z":{"proc":"zjets","label":"Z(#nu#nu)",'text':'Znn'},
        "W":{"proc":"wjets","label":"W(l#nu)",'text':'Wln'},
    },
    "Wen": {"proc":"wjets","label":"W(e#nu)",'text':'Wen'},
    "Wmn": {"proc":"wjets","label":"W(#mu#nu)",'text':'Wmn'},
    "Wln": {"proc":"SumOfBkg","label":"W(l#nu)",'text':'Wln'},
    "Zee": {"proc":"zll","label":"Z(ee)",'text':'Zee'},
    "Zmm": {"proc":"zll","label":"Z(#mu#mu)",'text':'Zmm'},
    "Zll": {"proc":"SumOfBkg","label":"Z(ll)",'text':'Zll'},
    "gjets": {"proc":"gjets","label":"#gamma","text":"G"},
}
def TF_DataStyle(tf,color):
    # tf.SetLineWidth(2)
    tf.SetMarkerColor(color)
    tf.SetMarkerStyle(20);
    tf.SetMarkerSize(1);
def TF_MCStyle(tf,color):
    tf.SetLineWidth(2)
    tf.SetLineColor(color)
def GetRMS(hs): return (sum(ibin*ibin for ibin in hs)/len(hs))*0.5
def GetStdDev(hs):
    rms = GetRMS(hs)
    return ( sum( (ibin - rms)**2 for ibin in hs)/(len(hs)-1) )**0.5
def compareOutput(fname1,fname2):
    tfile1 = TFile.Open(fname1)
    tfile2 = TFile.Open(fname2)

    def compare(bu,uw,region_num,region_den):
        def getTF(num,den,proc): return GetRatio(num[proc],den[proc])
        bu_data = getTF(bu[region_num],bu[region_den],'data')
        bu_mc = getTF(bu[region_num],bu[region_den],'SumOfBkg')
        uw_data = getTF(uw[region_num],uw[region_den],'data')
        uw_mc = getTF(uw[region_num],uw[region_den],'SumOfBkg')

        rname = "%s/%s"%(processMap[region_num]['label'],processMap[region_den]['label'])
        tfname = "Ratio_{%s}" % rname
        
        c = TCanvas("c", "canvas",800,800);
        gStyle.SetOptStat(0);
        gStyle.SetLegendBorderSize(0);
        # c.SetLeftMargin(0.15);
        #c.SetLogy();
        #c.cd();
        
        pad1 = TPad("pad1","pad1",0.01,0.25,0.99,0.99);
        pad1.Draw(); pad1.cd();
        pad1.SetFillColor(0);
        pad1.SetFrameBorderMode(0);
        pad1.SetBorderMode(0);
        pad1.SetBottomMargin(0.);

        TF_DataStyle(bu_data,kBlue)
        TF_MCStyle(bu_mc,kBlue)
        
        TF_DataStyle(uw_data,kRed)
        TF_MCStyle(uw_mc,kRed)

        max_rms = max( GetRMS(hs) for hs in (bu_data,bu_mc,uw_data,uw_mc) )
        max_std = max( GetStdDev(hs) for hs in (bu_data,bu_mc,uw_data,uw_mc) )

        nstd = 2
        bu_mc.SetMaximum(max_rms + nstd*max_std)
        bu_mc.SetMinimum(max(max_rms - nstd*max_std,0))

        bu_mc.SetTitle("")
        bu_mc.GetYaxis().SetTitle(tfname)

        bu_mc.Draw("hist")
        uw_mc.Draw("histsame")
        bu_data.Draw("pex0same")
        uw_data.Draw("pex0same")
        
        leg = getLegend(xmin=0.1,xmax=0.7,ymin=0.8,ymax=0.9)
        leg.SetNColumns(2)
        leg.AddEntry(bu_data,"%s BU Data" % rname,'p')
        leg.AddEntry(bu_mc,"%s BU MC" % rname,'l')
        leg.AddEntry(uw_data,"%s UW Data" % rname,'p')
        leg.AddEntry(uw_mc,"%s UW MC" % rname,'l')
        leg.Draw()
        
        c.cd()
        pad2 = TPad("pad2","pad2",0.01,0.01,0.99,0.25);
        pad2.Draw(); pad2.cd();
        pad2.SetFillColor(0); pad2.SetFrameBorderMode(0); pad2.SetBorderMode(0);
        pad2.SetTopMargin(0);
        pad2.SetBottomMargin(0.35);
        
        ratio_data = GetRatio(bu_data,uw_data)
        ratio_mc = GetRatio(bu_mc,uw_mc)
        
        RatioStyle(ratio_mc,xname="Recoil (GeV)",yname="BU/UW")
        RatioStyle(ratio_data,xname="Recoil (GeV)",yname="BU/UW")
        ratio_mc.SetLineColor(kBlack)
        ratio_data.SetLineColor(kBlack)
        ratio_data.SetMarkerColor(kBlack)
        ratio_mc.Draw("hist")
        ratio_data.Draw("pex0same")
        
        line = getRatioLine(ratio_data.GetXaxis().GetXmin(),ratio_data.GetXaxis().GetXmax())
        line.Draw("same");
        c.Update()

        fname = "%s%s_ratio" % (processMap[region_num]['text'],processMap[region_den]['text'])
        SaveAs(c,fname,year=config.version,sub="BU_Comparison/TransferFactors/")
        return 
    keylist1 =[ key.GetName() for key in  tfile1.GetListOfKeys()]
    keylist2 =[ key.GetName() for key in  tfile2.GetListOfKeys()]
    def SumOfBkg(sample):
        bkg = None
        for key,hs in sample.iteritems():
            if 'data' in key: continue

            if bkg is None: bkg = hs.Clone('SumOfBkg')
            else: bkg.Add(hs)
        sample['SumOfBkg'] = bkg
    def AddRegions(region1,region2):
        region_sum = {}
        for key in region1:
            hs1,hs2 = region1[key],region2[key]
            region_sum[key] = hs1.Clone()
            region_sum[key].Add(hs2)
        return region_sum
    bu,uw = {},{}
    for region in regionlist:
        bu[region] = { key.replace('%s_'%region,""):tfile1.Get(key) for key in keylist1 if region in key }
        uw[region] = { key.replace('%s_'%region,""):tfile2.Get(key) for key in keylist2 if region in key }
        SumOfBkg(bu[region])
        SumOfBkg(uw[region])
    for sample in (bu,uw):
        sample['Wln'] = AddRegions(sample['Wen'],sample['Wmn'])
        sample['Zll'] = AddRegions(sample['Zee'],sample['Zmm'])

    
    compare(bu,uw,'Wen','gjets')
    compare(bu,uw,'Zee','gjets')
    compare(bu,uw,'Zee','Wen')
    
    compare(bu,uw,'Wmn','gjets')
    compare(bu,uw,'Zmm','gjets')
    compare(bu,uw,'Zmm','Wmn')
    
    compare(bu,uw,'Wln','gjets')
    compare(bu,uw,'Zll','gjets')
    compare(bu,uw,'Zll','Wln')
    


compareOutput(parser.args.argv[0],parser.args.argv[1])
    
