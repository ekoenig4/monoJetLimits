for y in $YEARS; do

    python PlotTool/compareLimits1D.py -n Limits/${y}/recoil_${y}/recoil_${y}_nCRnSTATnSYS.sys/ -d \
	   Limits/${y}/recoil_${y}/recoil_${y}_nCRnSTAT.sys/ Limits/${y}/recoil_${y}/recoil_${y}_nSTAT.sys/
    
    python PlotTool/compareLimits1D.py -n Limits/${y}/ChNemPtFrac+0.5_${y}/ChNemPtFrac+0.5_${y}_nCRnSTATnSYS.sys/ -d \
	   Limits/${y}/ChNemPtFrac+0.5_${y}/ChNemPtFrac+0.5_${y}_nCRnSTAT.sys/ Limits/${y}/ChNemPtFrac+0.5_${y}/ChNemPtFrac+0.5_${y}_nSTAT.sys/

    python PlotTool/compareLimits1D.py -n Limits/${y}/ChNemPtFrac+0.5_${y}/ChNemPtFrac+0.5_${y}_nCRnSTATnSYS.sys/ -d \
	   Limits/${y}/ChNemPtFrac+0.5_${y}/ChNemPtFrac+0.5_${y}_nCRnPFUnSTAT.sys/ Limits/${y}/ChNemPtFrac+0.5_${y}/ChNemPtFrac+0.5_${y}_nPFUnSTAT.sys/
    
    python PlotTool/compareLimits1D.py -n Limits/${y}/ChNemPtFrac+0.5_${y}/ChNemPtFrac+0.5_${y}_nCRnSTATnSYS.sys/ -d \
	   Limits/${y}/ChNemPtFrac+0.5_${y}/ChNemPtFrac+0.5_${y}_nCRnJESnPFUnSTAT.sys/ Limits/${y}/ChNemPtFrac+0.5_${y}/ChNemPtFrac+0.5_${y}_nJESnPFUnSTAT.sys/
done
