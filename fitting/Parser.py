from argparse import ArgumentParser
parser = ArgumentParser()
parser.add_argument('argv',nargs='*',help='accumlate undefined arguments',default=[])
parser.add_argument('--debug',help='enable debug option',action='store_true',default=False)

def parse_args():
    if hasattr(parser,"args"): return
    parser.args = ArgumentParser.parse_args(parser)
    return parser.args
parser.parse_args = parse_args
