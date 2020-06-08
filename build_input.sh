
pushd Systematics/
python ../mergeSys.py -f 2017/recoil_2017.sys.root 2018/recoil_2018.sys.root -c category_monojet_2017 category_monojet_2018 -o monojet_recoil.sys.root
python ../addHiggsInvisible.py monojet_recoil.sys.root ../cards/bu/monojet/input/legacy_limit_monojet.root
popd
