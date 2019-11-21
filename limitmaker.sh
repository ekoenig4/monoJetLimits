
# YEARS="2018"
for y in $YEARS; do
    command="./makeWorkspace.py -i Systematics/${y}/ChNemPtFrac+0.5_${y}.sys.root";
    # $command --no-sys;
    # $command --no-stat;
    # $command ;
    # $command --cr;
    $command --cr --no-stat;
done
