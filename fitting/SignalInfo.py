from Parser import parser

axial = ['axial']
hinv = ["ggh","vbf","wh","zh"]
zprime = ["zprime"]
def signal_type(arg,varmap=vars()): return varmap[arg]
parser.add_argument("--signal",help="Specify signal to use for datacards and workspace",default=zprime,type=signal_type)


if __name__ == "__main__":
    parser.parse_args()
    print parser.args.signal
