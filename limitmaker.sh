
# ./makeWorkspace.py -i Systematics/2016/${1}_2016.sys.root --run2 --no-sys --no-cr --no-stat || exit 1
# ./makeWorkspace.py -i Systematics/2016/${1}_2016.sys.root --run2 --no-cr --no-stat &
./makeWorkspace.py -i Systematics/2016/${1}_2016.sys.root --run2 --no-stat || exit 1
./makeWorkspace.py -i Systematics/2016/${1}_2016.sys.root --run2 --no-stat --no-pfu &
for y in $YEARS; do
    command="./makeWorkspace.py -i Systematics/${y}/${1}_${y}.sys.root";
    # $command --no-sys --no-cr --no-stat &
    # $command --no-cr --no-stat &
    # $command --no-cr --no-stat --no-pfu &
    $command --no-stat --no-pfu &
    # $command --no-cr --no-stat --no-pfu --no-jes &
    # $command --no-stat --no-pfu --no-jes &
    $command --no-stat &
    # $command
done
