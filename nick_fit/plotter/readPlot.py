#!/usr/bin/env python
import ROOT
ROOT.gROOT.SetBatch(True)
ROOT.PyConfig.IgnoreCommandLineOptions = True
import argparse


def findHistograms(canvas):
    histList = []
    for prim in canvas.GetListOfPrimitives():
        if prim.GetName() == "stackPad":
            histList = findHistograms(prim)
        elif prim.ClassName() == "THStack":
            histList.extend([h for h in prim.GetHists()])
        elif prim.ClassName() == "TH1D":
            histList.append(prim)
    return histList


def findClosestBinRange(hist, low, high):
    # The same as SetRangeUser()
    ax = hist.GetXaxis()
    iFirst = ax.FindFixBin(low)
    iLast  = ax.FindFixBin(high)
    if ax.GetBinUpEdge(iFirst) <= low:
        iFirst += 1
    if ax.GetBinLowEdge(iLast) >= high:
        iLast -= 1
    # print "Low  bin: ", ax.GetBinLowEdge(iFirst), low
    # print "High bin: ", ax.GetBinUpEdge(iLast), high
    return (iFirst, iLast)


def main():
    parser = argparse.ArgumentParser(description="Makes plots and combine shapes from MonoZSelector output", formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    def rootFileType(fileName):
        f = ROOT.TFile.Open(fileName)
        if not f:
            msg = "%s is not a valid ROOT file or could not be opened!" % fileName
            raise argparse.ArgumentTypeError(msg)
        return f

    parser.add_argument("inputFile", help="Input file", type=rootFileType)
    parser.add_argument("--canvasName",  help="Canvas name (if unspecified, take first canvas in file)", default=None)
    parser.add_argument("--cut",  help="If specified, also compute stats with cut on x values (will choose closest inclusive bin boundary)", nargs=2, default=None)
    parser.add_argument("--format",  help="Output format", choices=["terminal", "csv", "latex"], default="terminal")

    args = parser.parse_args()


    if args.canvasName:
        canvas = args.inputFile.Get(canvasName)
    else:
        canvas = args.inputFile.GetListOfKeys()[0].ReadObj()

    plotName = canvas.GetName()
    allHists = findHistograms(canvas)
    rows = [
        ("PlotGroup", []),
        ("Title", []),
        ("Integral", []),
        ("Integral Unc.", []),
    ]
    if args.cut:
        rows.extend([
            ("Ranged Integral [%s to %s]" % tuple(args.cut), []),
            ("Ranged Integral Unc.", []),
        ])

    for hist in allHists:
        rows[0][1].append(hist.GetName().split("__")[-1])
        rows[1][1].append(hist.GetTitle())
        err = ROOT.Double(0.)
        rows[2][1].append(hist.IntegralAndError(0,-1, err))
        rows[3][1].append(err)
        if args.cut:
            cutRange = findClosestBinRange(hist, float(args.cut[0]), float(args.cut[1]))
            err = ROOT.Double(0.)
            rows[4][1].append(hist.IntegralAndError(cutRange[0], cutRange[1], err))
            rows[5][1].append(err)

    if args.format == "terminal":
        # TODO: steal https://github.com/kdlong/WZConfigPlotting/blob/allScales/Utilities/prettytable.py
        # and https://github.com/kdlong/WZConfigPlotting/blob/allScales/makeHistStack.py#L61-L104
        for col in range(len(allHists)):
            print "%s:" % rows[0][1][col]
            for row in rows:
                print "\t%s" % row[0], row[1][col]
    elif args.format == "csv":
        for row in rows:
            print ",".join(map(str, [row[0]] + row[1]))
    elif args.format == "latex":
        print "TODO"

if __name__ == "__main__":
    main()
