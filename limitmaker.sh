
# YEARS="2016"
for y in $YEARS; do
    command="./makeWorkspace.py -i Systematics/${y}/recoil_${y}.sys.root";
    $command --no-sys --no-cr --no-stat
    $command --no-cr --no-stat
    # $command --no-cr --no-stat --no-pfu
    # $command --no-stat --no-pfu
    # $command --no-cr --no-stat --no-pfu --no-jes
    # $command --no-stat --no-pfu --no-jes
    $command --no-stat
    # $command
done
