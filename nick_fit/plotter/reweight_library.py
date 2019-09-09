import logging
import re

log = logging.getLogger( 'reweight_library' )
def apply_binning(histo,bins=None):
   import array
   if not bins:
      bins = [0,100, 125, 150, 175, 200, 250, 300, 350, 400, 500, 600]
   nbins = len(bins)-1
   histo = histo.Rebin(nbins, histo.GetTitle() + "_rebin", array.array("d",bins))

   return histo


class XSReader():
   def __init__(self,path_to_file,template=None):
      import numpy
      self.data = numpy.loadtxt(path_to_file,dtype=str)
      self.template = template
      self.columns = self.data.shape[1]

   def get_xs(self,key):
      for entry in self.data:
         if entry[0] == key:
            return float(entry[1])
      log.error("No XS found for key '{0}'".format(key))
   def get_xs_from_pair(self,pair):
      for entry in self.data:
         if( self.template.format(mmed=pair[0], mdm=pair[1]) == entry[0] ):
             return float(entry[1])

   def set_template(self,template):
      self.template = template

def fix_overflow(histo):
   import math
   ### Overflow
   overflow_bin = histo.GetNbinsX()+1

   overflow = histo.GetBinContent(overflow_bin)
   overflow_unc = histo.GetBinError(overflow_bin)

   lastbin = histo.GetBinContent(overflow_bin-1)
   lastbin_unc = histo.GetBinError(overflow_bin-1)

   histo.SetBinContent(overflow_bin - 1, lastbin + overflow)
   histo.SetBinError(overflow_bin - 1, math.sqrt(pow(lastbin_unc,2) + pow(overflow_unc,2)))
   histo.SetBinContent(overflow_bin,0)
   histo.SetBinError(overflow_bin,0)

   ### Underflow
   underflow = histo.GetBinContent(0)
   underflow_unc = histo.GetBinError(0)

   firstbin = histo.GetBinContent(1)
   firstbin_unc = histo.GetBinError(1)

   histo.SetBinContent(1, firstbin + underflow)
   histo.SetBinError(1, math.sqrt(pow(firstbin_unc,2) + pow(underflow_unc,2)))
   histo.SetBinContent(0,0)
   histo.SetBinError(0,0)

   ### Clear to be sure
   histo.ClearUnderflowAndOverflow()

   return histo


### Helper function, finds out what DM signals are in the input file
def get_available_signals(infile):
   dmsimp = {}
   dmsimp["A"] = []
   dmsimp["V"] = []
   dmf = dmsimp
   for key in list(infile.GetListOfKeys()):
      name = key.GetName()
      if "DarkMatter" in name:
         if "NLO" in name:
            if "Vector" in name:
               dmsimp["V"].append(name)
            elif "Axial" in name:
               dmsimp["A"].append(name)
         else:
            if "Vector" in name:
               dmf["V"].append(name)
            elif "Axial" in name:
               dmf["A"].append(name)
   return dmsimp, dmf


### Helper function to convert a tag into a dataset
# See "get_lookup_table" for info
def convert_tag_to_dataset(tag):
   regex = re.compile("genmet_gdma(\d+\.\d+)_gdmv(\d+\.\d+)_gla(\d+\.\d+)_glv(\d+\.\d+)_gnu(\d+\.\d+)_gqa(\d+\.\d+)_gqv(\d+\.\d+)_mmed(\d+)_mdm(\d+)")

   m = regex.match(tag)
   if(m):
      gdma, gdmv, gla, glv, gnu, gqa, gqv, mmed, mdm = (float(x) for x in m.groups())
      mmed = int(mmed)
      mdm = int(mdm)
      if( gdma == 1.0 and gdmv == 0.0 and gqa == 0.25 and gqv == 0.0 ):
         return "DarkMatter_MonoZToLL_NLO_Axial_Mx-{mdm}_Mv-{mmed}_gDM1_gQ0p25_TuneCUETP8M1_13TeV-madgraph".format(mdm=mdm, mmed=mmed)
      elif( gdma == 0.0 and gdmv == 1.0 and gqa == 0.0 and gqv == 0.25 ):
         return "DarkMatter_MonoZToLL_NLO_Vector_Mx-{mdm}_Mv-{mmed}_gDM1_gQ0p25_TuneCUETP8M1_13TeV-madgraph".format(mdm=mdm, mmed=mmed)

   log.warning("Could not convert tag: '{0}'".format(tag))
   return None

### Helper function to create two-way lookup table
# tag <-> dataset, e.g.
# tag "gdma1.0_gdmv0.0_gla0.0_glv0.0_gnu0.0_gqa0.25_gqv0.0_mmed10000_mdm500"
# dataset "DarkMatter_MonoZToLL_NLO_Axial_Mx-{mdm}_Mv-{mmed}_gDM1_gQ0p25_TuneCUETP8M1_13TeV-madgraph"
def get_lookup_table(weightfile):
   tag_to_dataset = {}
   dataset_to_tag= {}
   for key in list(weightfile.GetListOfKeys()):
      tag = key.GetName()
      dataset = convert_tag_to_dataset(tag)
      if(dataset):
         tag_to_dataset[tag] = dataset
         dataset_to_tag[dataset] = tag
   return tag_to_dataset, dataset_to_tag

def extract_masses(dataset):
   #~ print dataset
   regex = re.compile("DarkMatter_MonoZToLL_NLO_{0}_Mx-(\d+)_Mv-(\d+)_gDM1_gQ0p25_TuneCUETP8M1_13TeV-madgraph".format("Axial" if "Axial" in dataset else "Vector"))
   #~ print regex.pattern
   m = regex.match(dataset)
   if(m):
      mdm, mmed = (int(x) for x in m.groups())
      return (mmed,mdm)
   else:
     log.error("Could not extract masses fordataset: '{0}'".format(dataset))

def find_reference(target, candidates):
   import math
   min_distance = 1e20
   closest_pair = 0
   #~ print target
   mmed_tgt, mdm_tgt = extract_masses(target)

   mode = 1
   if(mode == 1):
      for candidate in candidates["A" if "Axial" in target else "V"]:
         mmed_ref, mdm_ref = extract_masses(candidate)

         valid_choice = True
         # Must be different
         valid_choice = valid_choice and ( (mmed_tgt != mmed_ref) or (mdm_tgt != mdm_ref) )
         # Reference should have relatively higher mdm (bc spectrum is harder)
         valid_choice = valid_choice and (mdm_tgt / mmed_tgt <= mdm_ref / mmed_ref)

         if( not valid_choice ): continue


         distance = math.sqrt( pow(mmed_ref - mmed_tgt,2) + pow(mdm_ref - mdm_tgt,2) )
         if( distance < 1e-5 ): continue
         if( distance < min_distance ):
            min_distance = distance
            closest_pair = (mmed_ref,mdm_ref)

   if(not closest_pair):
      return 0
   else:
      reference = re.sub("Mx-[0-9]+","Mx-{0}".format(closest_pair[1]), target)
      reference = re.sub("Mv-[0-9]+","Mv-{0}".format(closest_pair[0]), reference)
      return reference

def get_weights(weight_file, tgt_tag, ref_tag, xs_gen, bins):

   numerator = weight_file.Get( tgt_tag ).Clone()
   denominator = weight_file.Get( ref_tag ).Clone()

   numerator=fix_overflow(numerator)
   numerator=apply_binning(numerator,bins)
   numerator=fix_overflow(numerator)
   denominator=fix_overflow(denominator)
   denominator=apply_binning(denominator,bins)
   denominator=fix_overflow(denominator)


   # Get Errors right
   #~ numerator.Sumw2()
   #~ denominator.Sumw2()

   weights = numerator.Clone()
   weights.Divide(denominator)
   weights.SetDirectory(0)

   # Cross-sections
   xs_tgt = xs_gen.get_xs(tgt_tag.replace("genmet_",""))
   xs_ref = xs_gen.get_xs(ref_tag.replace("genmet_",""))

   if(xs_tgt and xs_ref):
      weights.Scale( xs_tgt / xs_ref )
      return weights
   else: return None

### Takes a 2D histogram of Reco MET versus Gen MET
### and uses it to do a gen MET reweighting based on weights
# histo_2d:        TH2D, x axis = gen met, y axis = reco met
# histo_weights:   TH1D, x axis = gen met, bin content = weight
def get_reweighted_spectrum(histo_2d, histo_weights, bins):
   result = histo_weights.Clone("reweighted")
   result.Reset()
   result.SetDirectory(0)

   for xbin in range(1,histo_2d.GetNbinsX()+1):
      projection = histo_2d.ProjectionY("tmp", xbin, xbin)
      projection = apply_binning(projection,bins)
      projection = fix_overflow(projection)

      genmet = histo_2d.GetXaxis().GetBinCenter(xbin)

      weight_bin = histo_weights.FindBin(genmet)
      if( weight_bin > histo_weights.GetNbinsX() ): weight_bin = histo_weights.GetNbinsX()
      weight = histo_weights.GetBinContent(weight_bin)

      projection.Scale(weight)
      result.Add(projection)

   return result

def apply_ratio_to_2d_histogram(histo,ratio):
   new_histo = histo.Clone()
   new_histo.Reset()
   new_histo.SetDirectory(0)

   for xbin in range(1,histo.GetNbinsX()+1):
      for ybin in range(1,histo.GetNbinsX()+1):
         pfmet = histo.GetXaxis().GetBinCenter(xbin)

         ratio_bin = ratio.FindBin(pfmet)
         #~ ratio_bin = min( ratio_bin, ratio.GetNbinsX())
         if( ratio_bin >= ratio.GetNbinsX() ): ratio_bin = ratio.GetNbinsX()
         scale = ratio.GetBinContent(ratio_bin)

         old_content = histo.GetBinContent(xbin, ybin)
         old_unc = histo.GetBinError(xbin, ybin)
         new_histo.SetBinContent(xbin,ybin,scale * old_content )
         new_histo.SetBinError(xbin,ybin,scale * old_unc )
   return new_histo


