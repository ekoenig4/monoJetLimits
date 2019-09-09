#include <vector>
#include <utility>
#include <algorithm>
#include "TFile.h"
#include "TMath.h"
#include <boost/lexical_cast.hpp>
#include <boost/format.hpp>

void addTemplate(string procname, RooArgList& varlist, RooWorkspace& ws, TH1F* hist) {
  RooDataHist rhist(procname.c_str(), "", varlist, hist);
  ws.import(rhist);
}

void makeBinList(string procname, RooRealVar& var, RooWorkspace& ws, TH1F* hist, RooArgList& binlist, bool setConst = false) {
  for (int i = 1; i <= hist->GetNbinsX(); i++) {
    stringstream binss;
    binss << procname << "_bin" << i;
    RooRealVar* binvar;
    if (!setConst) binvar = new RooRealVar(binss.str().c_str(), "", hist->GetBinContent(i), 0.0, 2000.0);
    else           binvar = new RooRealVar(binss.str().c_str(), "", hist->GetBinContent(i));
    binlist.add(*binvar);
  }

  stringstream normss;
  normss << procname << "_norm";

  RooParametricHist phist(procname.c_str(), "", var, binlist, *hist);
  RooAddition norm(normss.str().c_str(), "", binlist);

  // ws.import(phist,RooFit::RecycleConflictNodes());
  ws.import(phist);
  ws.import(norm, RooFit::RecycleConflictNodes());

}


void makeBinList_halo(string procname, RooRealVar& var, RooWorkspace& ws, TH1F* hist, vector<pair<RooRealVar*, TH1*>> syst, RooArgList& binlist) {
  RooRealVar* mu_halo_monophHighPhi_scale = new RooRealVar("mu_halo_monophHighPhi_scale", "mu_halo_monophHighPhi_scale", 1.0, 0.0, 5.0);
  RooRealVar* shape_err = new RooRealVar("Halo_SR_above0p5_MIPTotalEnergy", "Halo_SR_above0p5_MIPTotalEnergy", 0.0, -5.0, 5.0);
  for (int i = 1; i <= hist->GetNbinsX(); i++) {
    stringstream rawmuss;
    rawmuss << procname << "_rawmu_bin" << i;
    RooRealVar* rawmu_bin = new RooRealVar(rawmuss.str().c_str(), "", hist->GetBinContent(i)); // Constant
    RooArgList fobinlist;
    fobinlist.add(*mu_halo_monophHighPhi_scale);
    fobinlist.add(*rawmu_bin);
    fobinlist.add(*shape_err);
    
    stringstream binss;
    binss << procname << "_bin" << i;
    stringstream formss;
    formss << "@0*@1";
    formss << "*(TMath::Power(1+" << hist->GetBinError(i)/hist->GetBinContent(i) << ", @2))";
    for (int j = 0; j < syst.size(); j++) {
      stringstream systbinss;
      if (syst[j].first == NULL) {
        systbinss << procname << "_" << syst[j].second->GetName() << "_bin" << i;
        RooRealVar* systbinvar = new RooRealVar(systbinss.str().c_str(), "", 0., -5., 5.);
        fobinlist.add(*systbinvar);
      }
      else {
        fobinlist.add(*syst[j].first);
      }
      formss << "*(TMath::Power(1+" << syst[j].second->GetBinContent(i) << ", @" << j+3 << "))";
    }
    RooFormulaVar* binvar = new RooFormulaVar(binss.str().c_str(), "", formss.str().c_str(), RooArgList(fobinlist));
    binlist.add(*binvar);
  }

  stringstream normss;
  normss << procname << "_norm";

  RooParametricHist phist(procname.c_str(), "", var, binlist, *hist);
  RooAddition norm(normss.str().c_str(), "", binlist);

  // ws.import(phist,RooFit::RecycleConflictNodes());
  ws.import(phist);
  ws.import(norm, RooFit::RecycleConflictNodes());

}
// ///////////////////////
// // RooProduct version
// ///////////////////////
// void makeBinList_halo(string procname, RooRealVar& var, RooWorkspace& ws, TH1F* hist, RooArgList& binlist) {
//   RooRealVar* mu_halo_monophHighPhi_scale = new RooRealVar("mu_halo_monophHighPhi_scale", "mu_halo_monophHighPhi_scale", 1.0, 0.0, 5.0);
//   for (int i = 1; i <= hist->GetNbinsX(); i++) {
//     stringstream rawmuss;
//     rawmuss << procname << "_rawmu_bin" << i;
//     stringstream prodss;
//     prodss << procname << "_prod_bin" << i;
//     RooRealVar* rawmu_bin = new RooRealVar(rawmuss.str().c_str(), "", hist->GetBinContent(i)); // Constant
//     RooProduct* binvar = new RooProduct(prodss.str().c_str(), "", RooArgSet(*mu_halo_monophHighPhi_scale,*rawmu_bin));
//     binlist.add(*binvar);
//   }

//   stringstream normss;
//   normss << procname << "_norm";

//   RooParametricHist phist(procname.c_str(), "", var, binlist, *hist);
//   RooAddition norm(normss.str().c_str(), "", binlist);

//   // ws.import(phist,RooFit::RecycleConflictNodes());
//   ws.import(phist);
//   ws.import(norm, RooFit::RecycleConflictNodes());

// }

void makeConnectedBinList(string procname, RooRealVar& var, RooWorkspace& ws, TH1F* rhist, vector<pair<RooRealVar*, TH1*>> syst, const RooArgList& srbinlist, RooArgList* crbinlist=NULL) {
  if (crbinlist == NULL) crbinlist = new RooArgList();

  for (int i = 1; i <= rhist->GetNbinsX(); i++) {
    stringstream rbinss;
    rbinss << "r_" << procname << "_bin" << i;
    RooRealVar* rbinvar = new RooRealVar(rbinss.str().c_str(), "", rhist->GetBinContent(i));

    stringstream rerrbinss;
    rerrbinss << procname << "_bin" << i << "_Runc";
    RooRealVar* rerrbinvar = new RooRealVar(rerrbinss.str().c_str(), "", 0., -5., 5.);

    stringstream binss;
    binss << procname << "_bin" << i;

    RooArgList fobinlist;
    fobinlist.add(srbinlist[i-1]);
    fobinlist.add(*rbinvar);
    fobinlist.add(*rerrbinvar);

    stringstream formss;
    formss << "@0/";
    formss << "(";
    formss << "@1";
    formss << "*(TMath::Power(1+" << rhist->GetBinError(i)/rhist->GetBinContent(i) << ", @2))";
    for (int j = 0; j < syst.size(); j++) {
      stringstream systbinss;
      if (syst[j].first == NULL) {
	systbinss << procname << "_" << syst[j].second->GetName() << "_bin" << i;
	RooRealVar* systbinvar = new RooRealVar(systbinss.str().c_str(), "", 0., -5., 5.);
	fobinlist.add(*systbinvar);
      }
      else {
	fobinlist.add(*syst[j].first);
      }
      formss << "*(TMath::Power(1+" << syst[j].second->GetBinContent(i) << ", @" << j+3 << "))";
    }
    formss << ")";

    RooFormulaVar* binvar = new RooFormulaVar(binss.str().c_str(), "", formss.str().c_str(), RooArgList(fobinlist));
    crbinlist->add(*binvar);
  }

  stringstream normss;
  normss << procname << "_norm";

  RooParametricHist phist(procname.c_str(), "", var, *crbinlist, *rhist);
  RooAddition norm(normss.str().c_str(),"", *crbinlist);

  ws.import(phist, RooFit::RecycleConflictNodes());
  ws.import(norm, RooFit::RecycleConflictNodes());
}

void makeConnectedBinList_noStatErr(string procname, RooRealVar& var, RooWorkspace& ws, TH1F* rhist, vector<pair<RooRealVar*, TH1*>> syst, const RooArgList& srbinlist, RooArgList* crbinlist=NULL) {
  if (crbinlist == NULL) crbinlist = new RooArgList();

  for (int i = 1; i <= rhist->GetNbinsX(); i++) {
    stringstream rbinss;
    rbinss << "r_" << procname << "_bin" << i;
    RooRealVar* rbinvar = new RooRealVar(rbinss.str().c_str(), "", rhist->GetBinContent(i));

    stringstream binss;
    binss << procname << "_bin" << i;

    RooArgList fobinlist;
    fobinlist.add(srbinlist[i-1]);
    fobinlist.add(*rbinvar);

    stringstream formss;
    formss << "@0/";
    formss << "(";
    formss << "@1";
    for (int j = 0; j < syst.size(); j++) {
      stringstream systbinss;
      if (syst[j].first == NULL) {
	systbinss << procname << "_" << syst[j].second->GetName() << "_bin" << i;
	RooRealVar* systbinvar = new RooRealVar(systbinss.str().c_str(), "", 0., -5., 5.);
	fobinlist.add(*systbinvar);
      }
      else {
	fobinlist.add(*syst[j].first);
      }
      formss << "*(TMath::Power(1+" << syst[j].second->GetBinContent(i) << ", @" << j+3 << "))";
    }
    formss << ")";

    RooFormulaVar* binvar = new RooFormulaVar(binss.str().c_str(), "", formss.str().c_str(), RooArgList(fobinlist));
    crbinlist->add(*binvar);
  }

  stringstream normss;
  normss << procname << "_norm";

  RooParametricHist phist(procname.c_str(), "", var, *crbinlist, *rhist);
  RooAddition norm(normss.str().c_str(),"", *crbinlist);

  ws.import(phist, RooFit::RecycleConflictNodes());
  ws.import(norm, RooFit::RecycleConflictNodes());
}

void getRegion(TDirectory* dir,RooWorkspace& ws,RooArgList& vars) {
  TH1F* data_obs = (TH1F*)dir->Get("data_obs");
  RooArgList binlist;
  addTemplate( ("data_obs_" + string(dir->GetName())).c_str(),vars,ws,data_obs );
}

void do_createWorkspace(string signal_samplename, bool connectWZ, vector<string> &signal_samplenames, vector<float> &signal_multipliers, string signal_histos_filename_stub, bool aTGC=false, float h3=0.0, float h4=0.0, vector<vector<vector<double>>> aTGC_2Dfits=vector<vector<vector<double>>>()){
  gSystem->Load("libHiggsAnalysisCombinedLimit.so");
  
  TFile *outfile = new TFile("workspace.root","RECREATE");
  RooWorkspace wspace("w","w");

  RooRealVar var("chnemptfrac","Ch + Nem P^{123}_{T} Fraction",0,1.1);
  RooArgList vars(var);

  // Templates
  TFile* systematics_file = new TFile("ChNemPtFrac_2016.sys.root");

  // ---------------------------- Signal Region ---------------------------------------------------------------------------//
  TDirectory* dir_sr = systematics_file->GetDirectory("sr");
  getRegion(dir_sr,wspace,vars);
  
  // ---------------------------- Write out the workspace -----------------------------------------------------------------//
  outfile->cd();
  wspace.Write();
  outfile->Close();
}
 

void createWorkspace(){
  bool connectWZ = true;
  

  vector<string> sample_names_DM_LO;
  sample_names_DM_LO.clear();


  vector<float> signal_multipliers_DM_LO;
  signal_multipliers_DM_LO.clear();
  
  do_createWorkspace("DM_LO_V_Mx-1_Mv-1000", connectWZ, sample_names_DM_LO, signal_multipliers_DM_LO, "DM_LO");
  
  
  
  // Printout for createDatacards.py
  
  cout<<"\n\n\n"<<endl;
  
  
  for(int i = 0; i < sample_names_DM_LO.size(); i++){
    if(i == 0)
      cout<<"DM_LO_samples_and_multipliers = {"<<"'"<<sample_names_DM_LO[i]<<"': '"<<signal_multipliers_DM_LO[i]<<"',"<<endl;
    else if(i == sample_names_DM_LO.size()-1)
      cout<<"'"<<sample_names_DM_LO[i]<<"': '"<<signal_multipliers_DM_LO[i]<<"'}"<<endl;
    else
      cout<<"'"<<sample_names_DM_LO[i]<<"': '"<<signal_multipliers_DM_LO[i]<<"',"<<endl;
  }
  

}
