# Based on Nicks code here
# https://gitlab.cern.ch/ncsmith/monoZ/blob/master/plotter/makeCards

class Datacard:
    def __init__(self):
        self.cards = {}
        self.nSignals = 0
    #####################
    def addChannel(self,channel):
        self.cards[channel] = {
            'shapes':[],
            'observation':[],
            'rates':[],
            'nuisances':{},
            'extras':set(),
            }
    #####################
    def write(self,makeGroups=False):
        for channel,card in self.cards.iteritems():
            with open("cards/card_%s" % channel,"w") as fout:
                # Headers
                fout.write("# Card for channel %s\n" % channel)
                fout.write("imax 1 # process in this card\n")
                fout.write("jmax %d # process in this card - 1\n" % (len(card["rates"])-1, ))
                fout.write("kmax %d # nuisances in this card\n" % len(card["nuisances"]))
                fout.write("-"*30 + "\n")
                for line in card["shapes"]:
                    fout.write(line+"\n")
                fout.write("-"*30 + "\n")
                for line in card["observation"]:
                    fout.write(line+"\n")
                fout.write("-"*30 + "\n")
                binLine = "{0:<40}".format("bin")
                procLine = "{0:<40}".format("process")
                indexLine = "{0:<40}".format("process")
                rateLine = "{0:<40}".format("rate")
                for i, tup in enumerate(card["rates"]):
                    binLine += "{0:>20}".format(channel)
                    procLine += "{0:>20}".format(tup[0])
                    indexLine += "{0:>20}".format(i - self.nSignals + 1)
                    rateLine += "{0:>20}".format("%.3f" % tup[1])
                for line in [binLine, procLine, indexLine, rateLine]:
                    fout.write(line+"\n")
                fout.write("-"*30 + "\n")
                for nuisance in sorted(card["nuisances"].keys()):
                    processScales = card["nuisances"][nuisance]
                    line = "{0:<40}".format(nuisance)
                    for process, _ in card["rates"]:
                        if process in processScales:
                            s = processScales[process]
                            if type(s) is tuple:
                                line += "{0:>20}".format("%.3f/%.3f" % s)
                            else:
                                line += "{0:>20}".format("%.3f" % s)
                        else:
                            line += "{0:>20}".format("-")
                    fout.write(line+"\n")
                if makeGroups:
                    def makeGroups(name, prefix):
                        group = [n.split(" ")[0] for n in card["nuisances"].keys() if prefix in n]
                        fout.write("%s group = %s\n" % (name, " ".join(group)))
                    makeGroups("theory", "Theo_")
                    makeGroups("mcStat", "Stat_")
                    makeGroups("CMS", "CMS_")
                for line in card["extras"]:
                    fout.write(line+"\n")

                
