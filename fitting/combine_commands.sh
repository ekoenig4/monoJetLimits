1;95;0cp# Copy the input histos
./copy_histos.sh

# Without halo fit:
root -l -q -b createWorkspaces_Pt_noHaloFit.C
combineCards.py -S SA=datacard_signal_above0p5_yesZW_noHaloFit.txt SB=datacard_signal_below0p5_noHaloFit.txt CR_ME=datacard_monoele.txt CR_MM=datacard_monomu.txt CR_DM=datacard_dimu.txt CR_DE=datacard_diele.txt > comb_card.txt

# With halo fit:
root -l -q -b createWorkspaces_Pt_HaloFit.C
combineCards.py -S SA=datacard_signal_above0p5_yesZW_halo.txt SB=datacard_signal_below0p5_halo.txt CR_ME=datacard_monoele.txt CR_MM=datacard_monomu.txt CR_DM=datacard_dimu.txt CR_DE=datacard_diele.txt > comb_card.txt


# Open comb_card.txt and replace workspace.root with a specific workspace name
# Then find the limit:
combine -M AsymptoticLimits comb_card.txt
