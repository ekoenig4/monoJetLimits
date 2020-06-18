gitlab="${CMSSW_BASE}/src/HiggsAnalysis/CombinedLimit/monoJetLimits/uw_mono-x_cards/monozprime/"

wsall="${CMSSW_BASE}/src/HiggsAnalysis/CombinedLimit/monoJetLimits/Limits/ChNemPtFrac/"
ws2017="${wsall}/ChNemPtFrac_2017.sys/"
ws2018="${wsall}/ChNemPtFrac_2018.sys/"
wscomb="${wsall}/ChNemPtFrac_Run2.sys/"

#----- Cards -----#
export_cards() {
    export_path=${gitlab}/cards
    mkdir -p ${export_path}
    
    cp -v ${ws2017}/cr_fit/datacard ${export_path}/card_monozprime_2017.txt
    cp -v ${ws2017}/cr_fit/datacard.root ${export_path}/card_monozprime_2017.root
    cp -v ${ws2017}/cr_fit/systematics.html ${export_path}/systematics_2017.html

    
    cp -v ${ws2018}/cr_fit/datacard ${export_path}/card_monozprime_2018.txt
    cp -v ${ws2018}/cr_fit/datacard.root ${export_path}/card_monozprime_2018.root
    cp -v ${ws2018}/cr_fit/systematics.html ${export_path}/systematics_2018.html
    
    cp -v ${wscomb}/cr_fit/datacard ${export_path}/card_monozprime_combined.txt
    cp -v ${wscomb}/cr_fit/datacard.root ${export_path}/card_monozprime_combined.root
}

#----- Diagnostics -----#
export_diagnostics() {
    export_path=${gitlab}/diagnostics
    mkdir -p ${export_path}
    
    cp -v ${ws2017}/cr_fit/fitDiagnostics_fit_CRonly_result.root ${export_path}/fitDiagnostics_monozprime_2017.root
    cp -v ${ws2017}/cr_fit/higgsCombine_fit_CRonly_result.FitDiagnostics.mH1000.root ${export_path}/higgsCombine_monozprime_2017.FitDiagnostics.mH1000.root
    cp -v ${ws2017}/cr_fit/diffNuisances_result.root ${export_path}/diffnuisances_monozprime_2017.root

    cp -v ${ws2018}/cr_fit/fitDiagnostics_fit_CRonly_result.root ${export_path}/fitDiagnostics_monozprime_2018.root
    cp -v ${ws2018}/cr_fit/higgsCombine_fit_CRonly_result.FitDiagnostics.mH1000.root ${export_path}/higgsCombine_monozprime_2018.FitDiagnostics.mH1000.root
    cp -v ${ws2018}/cr_fit/diffNuisances_result.root ${export_path}/diffnuisances_monozprime_2018.root
    
    cp -v ${wscomb}/cr_fit/fitDiagnostics_fit_CRonly_result.root ${export_path}/fitDiagnostics_monozprime_combined.root
    cp -v ${wscomb}/cr_fit/higgsCombine_fit_CRonly_result.FitDiagnostics.mH1000.root ${export_path}/higgsCombine_monozprime_combined.FitDiagnostics.mH1000.root
    cp -v ${wscomb}/cr_fit/diffNuisances_result.root ${export_path}/diffnuisances_monozprime_combined.root
}

#----- Impacts -----#
export_impacts() {
    export_path=${gitlab}/impacts
    mkdir -p ${export_path}
    
    cp -v ${ws2017}/impacts/impacts.pdf ${export_path}/impacts_monozprime_2017.pdf
    
    cp -v ${ws2018}/impacts/impacts.pdf ${export_path}/impacts_monozprime_2018.pdf
    
    cp -v ${wscomb}/impacts/impacts.pdf ${export_path}/impacts_monozprime_combined.pdf
}

#----- Input -----#
export_input() {
    export_path=${gitlab}/input
    mkdir -p ${export_path}
    
    cp -v Systematics/monozprime_ChNemPtFrac.sys.root ${export_path}/
}

export_cards
export_diagnostics
export_input
export_impacts
