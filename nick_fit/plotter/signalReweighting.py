#!/usr/bin/env python
#-*- coding:utf-8 -*-
from __future__ import division
import logging
import os.path
import argparse
import ROOT as r
import re
from reweight_library import *
log = logging.getLogger( 'signalReweighting' )

def parse_commandline():
   parser = argparse.ArgumentParser(description='Perform signal reweighting on MonoZSelector output.' \
                                                'The script assumes that the DM processes in the input file are all FullSim samples.' \
                                                'For all weights available in the weight file, it creates a new DM process by reweighting based on the FullSim processes in the input file.'
   )
   parser.add_argument('input_file', type=str,
                    help='input file.')

   parser.add_argument('--debug', type=str,metavar='LEVEL', default='INFO',
                    help='Set the debug level. Allowed values: ERROR, WARNING, INFO, DEBUG. [default = %default]' )
   parser.add_argument('--output', type=str, default="output.root",
                    help='Output file.')
   parser.add_argument('--weights', type=str,
                    help='Weight file.')
   parser.add_argument("--rebin", help="Specify alternate binning in comma-separated list", default=None)
   parser.add_argument("--control", help="Make control plots to check if everything is going well. Warning: This slows everything down A LOT.", action="store_true")
   parser.add_argument("--closure", help="Also reweight FullSim to FullSim for closure testing.", action="store_true")

   args = parser.parse_args()

   if(args.rebin):
      args.rebin = [float(x) for x in args.rebin.split(',')]
   format = '%(levelname)s (%(name)s) [%(asctime)s]: %(message)s'
   date = '%F %H:%M:%S'
   logging.basicConfig( level=logging._levelNames[ args.debug ], format=format, datefmt=date )


   return args

def set_style(histo,style):
   if(style==0):
      histo.SetFillColor(r.kOrange)
      histo.SetFillStyle(1001)
      histo.SetLineColor(r.kBlack)
   elif( style == 1):
      histo.SetMarkerStyle(20)
      histo.SetLineWidth(2)
      histo.SetLineColor(r.kRed)
      histo.SetMarkerColor(r.kRed)
   elif( style == 2):
      histo.SetMarkerStyle(20)
      histo.SetLineWidth(2)
      histo.SetLineColor(r.kBlue)
      histo.SetMarkerColor(r.kBlue)
   return histo

def do_dmsimp_reweighting(args):
   log.info("Reweighting DMSimp samples.")


   if(args.control):
      control_directory = "./control_plots/"
      if( not os.path.exists(control_directory)):
         os.makedirs(control_directory())
      log.info("Making control plots. They will be in '{0}'.".format(control_directory))

   ### Open files
   outfile = r.TFile(args.output,"RECREATE")
   infile = r.TFile(args.input_file)
   weightfile = r.TFile(args.weights)
   files = []
   files.append(infile)
   files.append(outfile)
   files.append(weightfile)


   try:
      for f in files:
         if(not f):
            raise Exception("File not opened properly!")

      dmsimp, dmf = get_available_signals(infile)
      tag_to_dataset, dataset_to_tag = get_lookup_table(weightfile)

      n_targets = len(dataset_to_tag)
      log.info('Reweighting {0} target datasets.'.format(n_targets))

      for count,target in enumerate(dataset_to_tag.keys()):
         if( count / n_targets % 0.1 == 0. ):
            log.info("Target {0} of {1}.".format(count, n_targets))
         ### Only perform reweighting of FullSim points if we specifically ask for closure testing
         this_is_closure = False
         if( target in dmsimp["A"] or target in dmsimp["V"] ):
            if( not args.closure ):
               continue
            else:
               log.info("Closure target detected: {0}".format(target))
               this_is_closure = True

         # Find reference and get weights
         reference = find_reference(target,dmsimp)

         if( not reference ):
            log.warning("No reference found. Skipping target '{0}'.".format(target))
            continue
         log.debug("Target / Reference: {0} / {1}".format(target,reference))
         xs_gen = XSReader("../data/dmsimp_gen_xs.txt")

         if (reference not in dataset_to_tag.keys()):
            raise Exception("Non-valid reference chosen. This should not happen.")
         weights = get_weights(weightfile,  dataset_to_tag[target], dataset_to_tag[reference],xs_gen, args.rebin)
         if( not weights ):
            log.warning("No weights found. Skipping target '{0}'.".format(target))
            continue

         met_2d_ref = infile.Get("{0}/ll_metRecoVGen".format(reference))
         met_spectrum_ref = fix_overflow(apply_binning(met_2d_ref.ProjectionY(""),args.rebin))
         met_spectrum_reweighted = fix_overflow(apply_binning(get_reweighted_spectrum(met_2d_ref, weights, args.rebin),args.rebin))

         ratio = met_spectrum_reweighted.Clone()
         ratio.Divide(met_spectrum_ref)

         if(args.control):
            c1 = r.TCanvas( 'c1','c1', 200, 10, 700, 500 )
            stack = r.THStack()
            stack.Add(set_style(weights,0), "HIST")
            stack.Add(set_style(ratio,1),"PE")
            stack.Draw("NOSTACK")
            c1.SaveAs("{0}/weight_{1}.pdf".format(control_directory,target))

            del c1
         # Write to output file
         directory = outfile.mkdir(target)

         histograms_to_reweight = ["ll_pfMet_systs","ll_pfMet_lheWeights"]
         for name in histograms_to_reweight:
            histo = infile.Get("{0}/{1}".format(reference,name)).Clone()
            histo.SetDirectory(0)
            reweighted = apply_ratio_to_2d_histogram(histo, ratio)
            reweighted.SetDirectory(directory)
            directory.Write()

            if(args.control and name == "ll_pfMet_systs"):
               c1 = r.TCanvas( 'c1','c1', 200, 10, 700, 500 )
               stack = r.THStack()
               stack.Add(set_style(fix_overflow(met_spectrum_ref),0), "HIST")
               stack.Add(set_style(fix_overflow(apply_binning(histo.ProjectionX("_px",1,1),args.rebin)),1), "PE")
               stack.SetTitle("2D v 1D before reweighting")
               stack.Draw("NOSTACK")
               c1.SaveAs("{0}/closure_1d_v_2d_before_{1}.pdf".format(control_directory,target))

               stack = r.THStack()
               print met_spectrum_reweighted
               stack.Add(set_style(met_spectrum_reweighted,0), "HIST")
               stack.Add(set_style(fix_overflow(apply_binning(reweighted.ProjectionX("_px",1,1),args.rebin)),1), "PE")
               stack.SetTitle("2D v 1D after reweighting")
               stack.Draw("NOSTACK")
               c1.SaveAs("{0}/closure_1d_v_2d_after_{1}.pdf".format(control_directory,target))
               del c1

         histograms_to_copy = ["selectorCounter", "counters"]
         for name in histograms_to_copy:
            histo = infile.Get("{0}/{1}".format(reference,name)).Clone()
            histo.SetDirectory(directory)
            directory.Write()

         directory.cd()
         reference_name = r.TNamed(reference, reference)
         reference_name.Write("referenceSample")
   finally:
      for f in files:
         if(f):
            f.Close()






def main():
   args = parse_commandline()
   do_dmsimp_reweighting(args)



if __name__ == '__main__':
   main()
