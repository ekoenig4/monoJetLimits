for y in $YEARS; do
    command="./makeWorkspace.py -i Systematics/${y}/ChNemPtFrac+0.5_${y}.sys.root";
    $command --no-sys;
    $command ;
    $command --cr;
done
