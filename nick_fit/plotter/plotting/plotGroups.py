from PlotGroup import PlotGroup
import re

# Imported by AnalysisResult.py to create a set of PlotGroup objects
# dict of name: (group, datasets)
# The AnalysisResult class will open each SelectorResult passed to it
# and look for matching datasets
allPlotGroups = {
    "Nonresonant": (
        PlotGroup("Nonresonant", "Nonresonant", PlotGroup.Stackable),
        [
            "ST_tW_top_5f_NoFullyHadronicDecays_13TeV-powheg_TuneCUETP8M1",
            "ST_tW_antitop_5f_NoFullyHadronicDecays_13TeV-powheg_TuneCUETP8M1",
            # "TTJets_DiLept_TuneCUETP8M1_13TeV-madgraphMLM-pythia8",
            "TTTo2L2Nu_TuneCUETP8M2_ttHtranche3_13TeV-powheg-pythia8",
            "WWTo2L2Nu_13TeV-powheg",
            "GluGluWWTo2L2Nu_HInt_MCFM_13TeV",
            "DYJetsToTauTau_ForcedMuEleDecay_M-50_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8",
        ]
    ),
    "DYTauTau": (
        PlotGroup("DYTauTau", "Z#rightarrow#tau_{l}#tau_{l}", PlotGroup.Stackable),
        [
            "DYJetsToTauTau_ForcedMuEleDecay_M-50_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8",
        ]
    ),
    "ZZ2l2nu": (
        PlotGroup("ZZ2l2nu", "ZZ#rightarrow2l2#nu", PlotGroup.Stackable),
        [
            "ZZTo2L2Nu_13TeV_powheg_pythia8",
            "ZZTo2L2Nu_13TeV_powheg_pythia8_ext1",
            "GluGluToContinToZZTo2e2nu_13TeV_MCFM701_pythia8",
            "GluGluToContinToZZTo2mu2nu_13TeV_MCFM701_pythia8",
        ]
    ),
    "qqZZ2l2nu": (
        PlotGroup("qqZZ2l2nu", "ZZ#rightarrow2l2#nu", PlotGroup.Stackable),
        [
            "ZZTo2L2Nu_13TeV_powheg_pythia8",
        ]
    ),
    "ggZZ2l2nu": (
        PlotGroup("ggZZ2l2nu", "ZZ#rightarrow2l2#nu", PlotGroup.Stackable),
        [
            "GluGluToContinToZZTo2e2nu_13TeV_MCFM701_pythia8",
            "GluGluToContinToZZTo2mu2nu_13TeV_MCFM701_pythia8",
        ]
    ),
    "ZZ2l2nuJetBinned": (
        PlotGroup("ZZ2l2nuJ", "ZZ#rightarrow2l2#nu", PlotGroup.SignalLike),
        [
            "ZZTo2L2Nu_0Jets_ZZOnShell_13TeV-amcatnloFXFX-madspin-pythia8",
            "ZZTo2L2Nu_1Jets_ZZOnShell_13TeV-amcatnloFXFX-madspin-pythia8",
            "ZZTo2L2Nu_2Jets_ZZOnShell_13TeV-amcatnloFXFX-madspin-pythia8",
            "GluGluToContinToZZTo2e2nu_13TeV_MCFM701_pythia8",
            "GluGluToContinToZZTo2mu2nu_13TeV_MCFM701_pythia8",
        ]
    ),
    "WZ3lnuJetBinned": (
        PlotGroup("WZ3lnu", "WZ#rightarrow 3l#nu (+EWK)", PlotGroup.Stackable),
        [
            "WLLJJ_WToLNu_EWK_TuneCUETP8M1_13TeV_madgraph-madspin-pythia8",
            "WZTo3LNu_0Jets_MLL-50_TuneCUETP8M1_13TeV-madgraphMLM-pythia8",
            "WZTo3LNu_1Jets_MLL-50_TuneCUETP8M1_13TeV-madgraphMLM-pythia8",
            "WZTo3LNu_2Jets_MLL-50_TuneCUETP8M1_13TeV-madgraphMLM-pythia8",
            "WZTo3LNu_3Jets_MLL-50_TuneCUETP8M1_13TeV-madgraphMLM-pythia8",
        ]
    ),
    "WZ3lnu": (
        PlotGroup("WZ3lnu", "WZ#rightarrow 3l#nu", PlotGroup.Stackable),
        [
            "WZTo3LNu_TuneCUETP8M1_13TeV-powheg-pythia8",
        ]
    ),
    "ZZ4l": (
        PlotGroup("ZZ4l", "ZZ#rightarrow4l", PlotGroup.Stackable),
        [
            "ZZTo4L_13TeV_powheg_pythia8",
            "GluGluToContinToZZTo2e2mu_13TeV_MCFM701_pythia8",
            "GluGluToContinToZZTo2e2tau_13TeV_MCFM701_pythia8",
            "GluGluToContinToZZTo2mu2tau_13TeV_MCFM701_pythia8",
            "GluGluToContinToZZTo4e_13TeV_MCFM701_pythia8",
            "GluGluToContinToZZTo4mu_13TeV_MCFM701_pythia8",
            "GluGluToContinToZZTo4tau_13TeV_MCFM701_pythia8",
        ]
    ),
    "qqZZ4l": (
        PlotGroup("qqZZ4l", "ZZ#rightarrow4l", PlotGroup.Stackable),
        [
            "ZZTo4L_13TeV_powheg_pythia8",
        ]
    ),
    "ggZZ4l": (
        PlotGroup("ggZZ4l", "ZZ#rightarrow4l", PlotGroup.Stackable),
        [
            "GluGluToContinToZZTo2e2mu_13TeV_MCFM701_pythia8",
            "GluGluToContinToZZTo2e2tau_13TeV_MCFM701_pythia8",
            "GluGluToContinToZZTo2mu2tau_13TeV_MCFM701_pythia8",
            "GluGluToContinToZZTo4e_13TeV_MCFM701_pythia8",
            "GluGluToContinToZZTo4mu_13TeV_MCFM701_pythia8",
            "GluGluToContinToZZTo4tau_13TeV_MCFM701_pythia8",
        ]
    ),
    "Other": (
        PlotGroup("Other2l", "Other bkg.", PlotGroup.Stackable),
        [
            "ST_t-channel_top_4f_inclusiveDecays_13TeV-powhegV2-madspin-pythia8_TuneCUETP8M1",
            "ST_t-channel_antitop_4f_inclusiveDecays_13TeV-powhegV2-madspin-pythia8_TuneCUETP8M1",
            "ST_s-channel_4f_leptonDecays_13TeV-amcatnlo-pythia8_TuneCUETP8M1",
            #
            "ZZTo2L2Q_13TeV_amcatnloFXFX_madspin_pythia8",
            "WZTo2L2Q_13TeV_amcatnloFXFX_madspin_pythia8",
            "ZGTo2LG_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8",
            "TTGJets_TuneCUETP8M1_13TeV-amcatnloFXFX-madspin-pythia8",
            "TTWJetsToLNu_TuneCUETP8M1_13TeV-amcatnloFXFX-madspin-pythia8",
            "TTWJetsToQQ_TuneCUETP8M1_13TeV-amcatnloFXFX-madspin-pythia8",
            "TTZToLLNuNu_M-10_TuneCUETP8M1_13TeV-amcatnlo-pythia8",
            "TTZToQQ_TuneCUETP8M1_13TeV-amcatnlo-pythia8",
            "tZq_ll_4f_13TeV-amcatnlo-pythia8",
            #
            "WWW_4F_TuneCUETP8M1_13TeV-amcatnlo-pythia8",
            "WWZ_TuneCUETP8M1_13TeV-amcatnlo-pythia8",
            "WZZ_TuneCUETP8M1_13TeV-amcatnlo-pythia8",
            "ZZZ_TuneCUETP8M1_13TeV-amcatnlo-pythia8",
            #
            "ZZTo4L_13TeV_powheg_pythia8",
            "GluGluToContinToZZTo2e2mu_13TeV_MCFM701_pythia8",
            "GluGluToContinToZZTo2e2tau_13TeV_MCFM701_pythia8",
            "GluGluToContinToZZTo2mu2tau_13TeV_MCFM701_pythia8",
            "GluGluToContinToZZTo4e_13TeV_MCFM701_pythia8",
            "GluGluToContinToZZTo4mu_13TeV_MCFM701_pythia8",
            "GluGluToContinToZZTo4tau_13TeV_MCFM701_pythia8",
        ]
    ),
    "Other3l": (
        PlotGroup("Other3l", "Other bkg.", PlotGroup.Stackable),
        [
            "ST_t-channel_top_4f_inclusiveDecays_13TeV-powhegV2-madspin-pythia8_TuneCUETP8M1",
            "ST_t-channel_antitop_4f_inclusiveDecays_13TeV-powhegV2-madspin-pythia8_TuneCUETP8M1",
            "ST_s-channel_4f_leptonDecays_13TeV-amcatnlo-pythia8_TuneCUETP8M1",
            #
            "ZZTo2L2Q_13TeV_amcatnloFXFX_madspin_pythia8",
            "WZTo2L2Q_13TeV_amcatnloFXFX_madspin_pythia8",
            "TTGJets_TuneCUETP8M1_13TeV-amcatnloFXFX-madspin-pythia8",
            "TTWJetsToLNu_TuneCUETP8M1_13TeV-amcatnloFXFX-madspin-pythia8",
            "TTWJetsToQQ_TuneCUETP8M1_13TeV-amcatnloFXFX-madspin-pythia8",
            "TTZToLLNuNu_M-10_TuneCUETP8M1_13TeV-amcatnlo-pythia8",
            "TTZToQQ_TuneCUETP8M1_13TeV-amcatnlo-pythia8",
            "tZq_ll_4f_13TeV-amcatnlo-pythia8",
            #
            "WWW_4F_TuneCUETP8M1_13TeV-amcatnlo-pythia8",
            "WWZ_TuneCUETP8M1_13TeV-amcatnlo-pythia8",
            "WZZ_TuneCUETP8M1_13TeV-amcatnlo-pythia8",
            "ZZZ_TuneCUETP8M1_13TeV-amcatnlo-pythia8",
            #
            "ZZTo2L2Nu_13TeV_powheg_pythia8",
            "GluGluToContinToZZTo2e2nu_13TeV_MCFM701_pythia8",
            "GluGluToContinToZZTo2mu2nu_13TeV_MCFM701_pythia8",
            "ZZTo4L_13TeV_powheg_pythia8",
            "GluGluToContinToZZTo2e2mu_13TeV_MCFM701_pythia8",
            "GluGluToContinToZZTo2e2tau_13TeV_MCFM701_pythia8",
            "GluGluToContinToZZTo2mu2tau_13TeV_MCFM701_pythia8",
            "GluGluToContinToZZTo4e_13TeV_MCFM701_pythia8",
            "GluGluToContinToZZTo4mu_13TeV_MCFM701_pythia8",
            "GluGluToContinToZZTo4tau_13TeV_MCFM701_pythia8",
        ]
    ),
    "Other4l": (
        PlotGroup("Other4l", "Other bkg.", PlotGroup.Stackable),
        [
            "ST_t-channel_top_4f_inclusiveDecays_13TeV-powhegV2-madspin-pythia8_TuneCUETP8M1",
            "ST_t-channel_antitop_4f_inclusiveDecays_13TeV-powhegV2-madspin-pythia8_TuneCUETP8M1",
            "ST_s-channel_4f_leptonDecays_13TeV-amcatnlo-pythia8_TuneCUETP8M1",
            #
            "ZZTo2L2Q_13TeV_amcatnloFXFX_madspin_pythia8",
            "WZTo2L2Q_13TeV_amcatnloFXFX_madspin_pythia8",
            "ZGTo2LG_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8",
            "TTGJets_TuneCUETP8M1_13TeV-amcatnloFXFX-madspin-pythia8",
            "TTWJetsToLNu_TuneCUETP8M1_13TeV-amcatnloFXFX-madspin-pythia8",
            "TTWJetsToQQ_TuneCUETP8M1_13TeV-amcatnloFXFX-madspin-pythia8",
            "TTZToLLNuNu_M-10_TuneCUETP8M1_13TeV-amcatnlo-pythia8",
            "TTZToQQ_TuneCUETP8M1_13TeV-amcatnlo-pythia8",
            "tZq_ll_4f_13TeV-amcatnlo-pythia8",
            #
            "WWW_4F_TuneCUETP8M1_13TeV-amcatnlo-pythia8",
            "WWZ_TuneCUETP8M1_13TeV-amcatnlo-pythia8",
            "WZZ_TuneCUETP8M1_13TeV-amcatnlo-pythia8",
            "ZZZ_TuneCUETP8M1_13TeV-amcatnlo-pythia8",
            #
            "WZTo3LNu_TuneCUETP8M1_13TeV-powheg-pythia8",
            # For extra stats use LO DY
            "DYJetsToLL_M-50_TuneCUETP8M1_13TeV-madgraphMLM-pythia8",
            "DYJetsToLL_Zpt-100to200_M-50_TuneCUETP8M1_13TeV-madgraphMLM-pythia8",
            "DYJetsToLL_Zpt-200toInf_M-50_TuneCUETP8M1_13TeV-madgraphMLM-pythia8",
        ]
    ),
    "DrellYan": (
        PlotGroup("DrellYan", "Z+Jets", PlotGroup.Stackable),
        [
            "DYJetsToLL_M-10to50_TuneCUETP8M1_13TeV-madgraphMLM-pythia8",
            "DYJetsToLL_M-50_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8",
        ]
    ),
    "DrellYanBinned": (
        PlotGroup("DrellYan", "Z+Jets", PlotGroup.Stackable),
        [
            "DYJetsToLL_M-10to50_TuneCUETP8M1_13TeV-madgraphMLM-pythia8",
            "DYJetsToLL_M-50_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8",
            "DYJetsToLL_Pt-50To100_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8",
            "DYJetsToLL_Pt-100To250_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8",
            "DYJetsToLL_Pt-250To400_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8",
            "DYJetsToLL_Pt-400To650_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8",
            "DYJetsToLL_Pt-650ToInf_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8",
        ]
    ),
    "DrellYanJetBinned": (
        PlotGroup("DrellYan", "Z+Jets", PlotGroup.Stackable),
        [
            "DYJetsToLL_M-10to50_TuneCUETP8M1_13TeV-madgraphMLM-pythia8",
            "DYToLL_0J_13TeV-amcatnloFXFX-pythia8",
            "DYToLL_1J_13TeV-amcatnloFXFX-pythia8",
            "DYToLL_2J_13TeV-amcatnloFXFX-pythia8",
        ]
    ),
    "DrellYanLO": (
        PlotGroup("DrellYan", "Z+Jets", PlotGroup.Stackable),
        [
            "DYJetsToLL_M-10to50_TuneCUETP8M1_13TeV-madgraphMLM-pythia8",
            "DYJetsToLL_M-50_TuneCUETP8M1_13TeV-madgraphMLM-pythia8",
            "DYJetsToLL_Zpt-100to200_M-50_TuneCUETP8M1_13TeV-madgraphMLM-pythia8",
            "DYJetsToLL_Zpt-200toInf_M-50_TuneCUETP8M1_13TeV-madgraphMLM-pythia8",
        ]
    ),
    # Use LO for more stats (no neg. weights) for non-prompt bkg. in WZ control region
    "NonPromptDY": (
        PlotGroup("NonPromptDY", "Z+Jets", PlotGroup.Stackable),
        [
            "DYJetsToLL_M-10to50_TuneCUETP8M1_13TeV-madgraphMLM-pythia8",
            "DYJetsToLL_M-50_TuneCUETP8M1_13TeV-madgraphMLM-pythia8",
            "DYJetsToLL_Zpt-100to200_M-50_TuneCUETP8M1_13TeV-madgraphMLM-pythia8",
            "DYJetsToLL_Zpt-200toInf_M-50_TuneCUETP8M1_13TeV-madgraphMLM-pythia8",
        ]
    ),
    "DrellYanEWK": (
        PlotGroup("DrellYanEWK", "Z EWK", PlotGroup.Stackable),
        [
            "EWK_LLJJ_MLL-50_MJJ-120_13TeV-madgraph-pythia8",
        ]
    ),
    "ZGamma": (
        PlotGroup("ZGamma", "Z+#gamma", PlotGroup.Stackable),
        [
            "ZGTo2LG_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8",
        ]
    ),
    "WJets": (
        PlotGroup("WJets", "W+Jets", PlotGroup.Stackable),
        [
            "WJetsToLNu_TuneCUETP8M1_13TeV-madgraphMLM-pythia8",
        ]
    ),
    "Data": (
        PlotGroup("Data", "Data", PlotGroup.Data),
        [
            "SingleMuon",
            "SingleElectron",
            "DoubleMuon",
            "DoubleEG",
            "MuonEG",
        ]
    ),
    "Asimov": (
        PlotGroup("Data", "Asimov Data", PlotGroup.Data),
        []
    ),
}


# Mainly for signals with a billion mass points
def parseSpecialPlotGroup(name):
    simplifiedModelRegex = re.compile(r"DM(\d+)M([VA])(\d+)")
    m = simplifiedModelRegex.match(name)
    if m:
        # TODO: title using m_{#chi}, etc. or not?
        title = "DM({0})M{1}({2})".format(*m.groups())
        plotGroup = PlotGroup(name, title, PlotGroup.SignalLike)
        datasets = [
            "DarkMatter_MonoZToLL_{1}_Mx-{0}_Mv-{2}_gDMgQ-1_TuneCUETP8M1_13TeV-madgraph".format(*m.groups())
        ]
        return (plotGroup, datasets)

    simplifiedModelNLOVARegex = re.compile(r"DM(\d+)M(nloDM[SPVA]|nloggToDM[SP]|nloppToDM[SP]|[01]jDM[SP]|SMM|nloSMM|)(\d+)")
    m = simplifiedModelNLOVARegex.match(name)
    if m:
        # TODO: title using m_{#chi}, etc. or not?
        title = "DM({0})M{1}({2})".format(*m.groups())
        plotGroup = PlotGroup(name, title, PlotGroup.SignalLike)
        if 'nloDMS' in title : 
            datasets = [
                "DarkMatter_MonoZToLL_NLO_Scalar_Mx-{0}_Mv-{2}_gDM1_gQ1_TuneCUETP8M1_13TeV-madgraph".format(*m.groups())
                ]
        elif 'nloggToDM' in title :
            datasets = [
                "DMSimp_MonoZLL_{med}_NoTau_MY0-{mmed}_mxd-{mdm}_qcut24".format(mdm=m.groups()[0], mmed=m.groups()[2], med=m.groups()[1][-1])
                ]
        elif 'nloppToDM' in title :
            datasets = [
                "DMSimp_MonoZLL_{med}_NoTau_AllInitial_MY0-{mmed}_mxd-{mdm}_qcut24".format(mdm=m.groups()[0], mmed=m.groups()[2], med=m.groups()[1][-1])
                ]
        elif 'jDM' in title :
            datasets = [
                "DMSimp_MonoZLL_{med}_NoTau_{j}Jet_MY0-{mmed}_mxd-{mdm}_qcut20".format(mdm=m.groups()[0], mmed=m.groups()[2], med=m.groups()[1][-1], j=m.groups()[1][0])
                ]
        elif 'nloDMP' in title : 
            datasets = [
                "DarkMatter_MonoZToLL_NLO_Pseudo_Mx-{0}_Mv-{2}_gDM1_gQ1_TuneCUETP8M1_13TeV-madgraph".format(*m.groups())
                ]
        elif 'nloDMV' in title :
             datasets = [
                "DarkMatter_MonoZToLL_NLO_Vector_Mx-{0}_Mv-{2}_gDM1_gQ0p25_TuneCUETP8M1_13TeV-madgraph".format(*m.groups())
                ]
        elif 'nloDMA' in title : 
            datasets = [
                "DarkMatter_MonoZToLL_NLO_Axial_Mx-{0}_Mv-{2}_gDM1_gQ0p25_TuneCUETP8M1_13TeV-madgraph".format(*m.groups())
                ]
        elif 'nloSMM' in title : 
            datasets = [
                "DarkMatter_MonoZToLL_NLO_SMM_Mx-{0}_Mv-{2}_gDM1_gQ1_TuneCUETP8M1_13TeV-madgraph".format(*m.groups())
                ]
        elif 'SMM' in title : 
            datasets = [
                "SMM_MonoZ_Mphi-{2}_Mchi-{0}_gSM-1p0_gDM-1p0_13TeV-madgraph".format(*m.groups())
                ]
        return (plotGroup, datasets)
    
    UnpartRegex = re.compile(r"DU(\d+)p(\d+)")
    m = UnpartRegex.match(name)
    if m:
        title = "Unparticle dU({0}p{1})".format(*m.groups())
        plotGroup = PlotGroup(name, title, PlotGroup.SignalLike)
        datasets = [
            "Unpart_ZToLL_SU-0_dU-{0}p{1}_LU-15_TuneCUETP8M1_13TeV-pythia8".format(*m.groups())
        ]
        return (plotGroup, datasets)
    
    ADDRegex = re.compile(r"MD(\d+)d(\d+)")
    m = ADDRegex.match(name)
    if m:
        title = "ADD MD({0})d{1}".format(*m.groups())
        plotGroup = PlotGroup(name, title, PlotGroup.SignalLike)
        if m.groups()[0] == '3':
            datasets = ["ADDMonoZ_ZToLL_MD-{0}_d-{1}_TuneCUETP8M1_13TeV-pythia8".format(*m.groups())]
        else:
            datasets = ["ADDMonoZ_ZtoLL_MD-{0}_d-{1}_TuneCUETP8M1_13TeV-pythia8".format(*m.groups())]

        return (plotGroup, datasets)


    zhInvisibleRegex = re.compile(r"(qq|gg|)ZH(\d+)")
    m = zhInvisibleRegex.match(name)
    if m:
        title = name
        plotGroup = PlotGroup(name, title, PlotGroup.SignalLike)
        proc, mass = m.groups()
        if mass == "125":
            datasets = []
            if proc == "gg" or proc == "":
                datasets.append("ggZH_HToInv_ZToLL_M125_13TeV_powheg_pythia8")
            if proc == "qq" or proc == "":
                datasets.append("ZH_ZToEE_HToInvisible_M125_13TeV_powheg_pythia8")
                datasets.append("ZH_ZToMM_HToInvisible_M125_13TeV_powheg_pythia8")
        else:
            datasets = [
                "ZH_ZToEE_HToInvisible_M%s_13TeV_powheg_pythia8" % mass,
                "ZH_ZToMM_HToInvisible_M%s_13TeV_powheg_pythia8" % mass,
            ]
        return (plotGroup, datasets)

    if name == "ZZJJ":
        plotGroup = PlotGroup(name, "ZZ EWK", PlotGroup.SignalLike)
        datasets = ["ZZJJ_ZZTo2L2Nu_EWK_13TeV-madgraph-pythia8"]
        return (plotGroup, datasets)

    return (None, None)
