
build() {
    python ../mergeSys.py -f 2016/${1}_2016.sys.root 2017/${1}_2017.sys.root 2018/${1}_2018.sys.root -c category_monozprime_201{6..8} -o monozprime_${1}.sys.root
}

pushd Systematics/
build ChNemPtFrac
# build ChNemPtFrac+0.1
# build ChNemPtFrac+0.3
# build ChNemPtFrac+0.5
# build recoil_ChNemPtFrac+0.7
# build recoil_ChNemPtFrac+0.8
# build recoil_ChNemPtFrac+0.85
# build recoil_ChNemPtFrac+0.9
popd
