emStack="--stack WZ3lnuJetBinned,Other,Nonresonant"
sigStack="--stack ggZZ2l2nu,qqZZ2l2nu,WZ3lnuJetBinned,Other,Nonresonant,DrellYanLO,DrellYanEWK"
lumiResult="--lumi 35867 ZZEWKSelector-24Apr2017_noDM.root --noVVDYcr --noNRBinflate --asimov"
rm -rf cards
mkdir cards
./makeCards $lumiResult --rebin 80,600 $emStack -c em
./makeCards $lumiResult --rebin 80,600 $sigStack --signal ZZJJ -c ee -c mm
combineCards.py -S $(for c in cards/*; do echo ${c##cards/card_}=$c; done) > card_combined.dat
text2workspace.py card_combined.dat
combine -M ProfileLikelihood card_combined.dat.root --expectSignal=1 -t -1 --significance
