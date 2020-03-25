gitlab="${CMSSW_BASE}/src/HiggsAnalysis/CombinedLimit/cards/uw/monojet/"

wsall="${CMSSW_BASE}/src/HiggsAnalysis/CombinedLimit/monoJetLimits/Limits/recoil/"
ws2017="${wsall}/recoil_2017.sys/"
ws2018="${wsall}/recoil_2018.sys/"
wscomb="${wsall}/recoil_Run2.sys/"

#----- Cards -----#
export_cards() {
    export_path=${gitlab}/cards
    mkdir -p ${export_path}
    
    cp -v ${ws2017}/cr_fit/datacard ${export_path}/card_monojet_2017.txt
    cp -v ${ws2017}/cr_fit/datacard.root ${export_path}/card_monojet_2017.root
    cp -v ${ws2017}/cr_fit/systematics.html ${export_path}/systematics_2017.html

    
    cp -v ${ws2018}/cr_fit/datacard ${export_path}/card_monojet_2018.txt
    cp -v ${ws2018}/cr_fit/datacard.root ${export_path}/card_monojet_2018.root
    cp -v ${ws2018}/cr_fit/systematics.html ${export_path}/systematics_2018.html
    
    cp -v ${wscomb}/cr_fit/datacard ${export_path}/card_monojet_combined.txt
    cp -v ${wscomb}/cr_fit/datacard.root ${export_path}/card_monojet_combined.root
}

#----- Diagnostics -----#
export_diagnostics() {
    export_path=${gitlab}/diagnostics
    mkdir -p ${export_path}
    
    cp -v ${ws2017}/cr_fit/fitDiagnostics_fit_CR_only_result.root ${export_path}/fitDiagnostics_monojet_2017.root
    cp -v ${ws2017}/cr_fit/higgsCombine_fit_CRonly_result.FitDiagnostics.mH1000.root ${export_path}/higgsCombine_monojet_2017.FitDiagnostics.mH1000.root
    cp -v ${ws2017}/cr_fit/diffNuisances_result.root ${export_path}/diffnuisances_monojet_2017.root

    cp -v ${ws2018}/cr_fit/fitDiagnostics_fit_CR_only_result.root ${export_path}/fitDiagnostics_monojet_2018.root
    cp -v ${ws2018}/cr_fit/higgsCombine_fit_CRonly_result.FitDiagnostics.mH1000.root ${export_path}/higgsCombine_monojet_2018.FitDiagnostics.mH1000.root
    cp -v ${ws2018}/cr_fit/diffNuisances_result.root ${export_path}/diffnuisances_monojet_2018.root
    
    cp -v ${wscomb}/cr_fit/fitDiagnostics_fit_CR_only_result.root ${export_path}/fitDiagnostics_monojet_combined.root
    cp -v ${wscomb}/cr_fit/higgsCombine_fit_CRonly_result.FitDiagnostics.mH1000.root ${export_path}/higgsCombine_monojet_combined.FitDiagnostics.mH1000.root
    cp -v ${wscomb}/cr_fit/diffNuisances_result.root ${export_path}/diffnuisances_monojet_combined.root
}

#----- Impacts -----#
export_impacts() {
    export_path=${gitlab}/impacts
    mkdir -p ${export_path}
    
    cp -v ${ws2017}/impacts/impacts.pdf ${export_path}/impacts_monojet_2017.pdf
    
    cp -v ${ws2018}/impacts/impacts.pdf ${export_path}/impacts_monojet_2018.pdf
    
    cp -v ${wscomb}/impacts/impacts.pdf ${export_path}/impacts_monojet_combined.pdf
}

#----- Input -----#
export_input() {
    export_path=${gitlab}/input
    mkdir -p ${export_path}
    
    cp -v Systematics/monojet_recoil.sys.root ${export_path}/
}

export_cards
export_diagnostics
export_input
# export_impacts
