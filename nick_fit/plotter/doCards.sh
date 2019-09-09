emStack="--stack Nonresonant,qqZZ2l2nu,ggZZ2l2nu,WZ3lnu,Other"
lllStack="--stack WZ3lnu,ZGamma,Other3l,NonPromptDY"
llllStack="--stack qqZZ4l,ggZZ4l,Other4l"
sigStack="--stack Nonresonant,qqZZ2l2nu,ggZZ2l2nu,WZ3lnu,Other,DrellYanBinned"
lumiResult="--lumi 35867 MonoZSelector-24Apr2017-gda44266.root MonoZSelector-DmSimp_Pseudo.root"
rm -rf cards
mkdir cards
rm -rf shapePlots/*
./makeCards    $lumiResult --rebin 100,400 $emStack -c em
./makeCards    $lumiResult --rebin 100,125,150,175,200,250,300,350,400,500,600 $lllStack -c lll
./makeCards    $lumiResult --rebin 100,125,150,175,200,250,300,350,400,500,600 $llllStack -c llll
if ./makeCards $lumiResult --rebin 50,100,125,150,175,200,250,300,350,400,500,600  $sigStack $@ -c ll
then
  cp shapePlots/* ~/www/monoZ/shapePlots/
  combineCards.py -S $(for c in cards/*; do echo ${c##cards/card_}=$c; done) > card_combined.dat
  text2workspace.py card_combined.dat
  combine -M Asymptotic card_combined.dat.root
else
  echo "Skipping $@"
fi
