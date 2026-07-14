import argparse


def __str2bool(v):
    if isinstance(v, bool):
        return v
    if v.lower() in ("yes", "y", "true", "t", "1"):
        return True
    if v.lower() in ("no", "n", "false", "f", "0"):
        return False
    raise argparse.ArgumentTypeError("Boolean value expected.")

def help():
    print("Helping...")

def init():
    print("Initializing environment...")

def main():
    parser = argparse.ArgumentParser()
    subparser = parser.add_subparsers(dest='command', required=True)

    help_parser = subparser.add_parser('help', help="Show help")
    help_parser.set_defaults(func=lambda args: help())

    init_parser = subparser.add_parser('init', help='Initializes AutoDocs on a local environment.')
    init_parser.add_argument('-c', '--commits', type=__str2bool, default=True, help='Include git commit msg generation')
    init_parser.add_argument('-u', '--umls', type=__str2bool, default=True, help='Include rendering uml diagrams from code')
    init_parser.set_defaults(func=lambda args: init())

    args = parser.parse_args()
    args.func(args)

if __name__ == '__main__':
    main()
