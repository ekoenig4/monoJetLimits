
pushd Systematics/
python ../mergeSys.py -f 2017/ChNemPtFrac_2017.sys.root 2018/ChNemPtFrac_2018.sys.root -c category_monozprime_2017 category_monozprime_2018 -o monozprime_ChNemPtFrac.sys.root
popd
