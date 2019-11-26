
# YEARS="2018"
for y in $YEARS; do
    command="./makeWorkspace.py -i Systematics/${y}/ChNemPtFrac+0.5_${y}.sys.root";
    $command --no-sys --no-cr --no-stat
    $command --no-cr --no-stat
    $command --no-stat
done
