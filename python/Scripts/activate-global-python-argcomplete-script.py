# PYTHON_ARGCOMPLETE_OK

# Copyright 2012-2013, Andrey Kislyuk and argcomplete contributors.
# Licensed under the Apache License. See https://github.com/kislyuk/argcomplete for more info.

'''
Activate the generic bash-completion script for the argcomplete module.
'''

import os, sys, argparse, argcomplete, shutil

parser = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)

dest_opt = parser.add_argument("--dest", help="Specify the bash completion modules directory to install into", default="/etc/bash_completion.d")
parser.add_argument("--user", help="Install into user directory (~/.bash_completion.d/)", action='store_true')
argcomplete.autocomplete(parser)
args = parser.parse_args()

if args.user:
    args.dest = os.path.expanduser("~/.bash_completion.d/")
    if not os.path.exists(args.dest):
        try:
            os.mkdir(args.dest)
        except Exception as e:
            parser.error("Path {d} does not exist and could not be created: {e}".format(d=args.dest, e=e))
elif not os.path.exists(args.dest) and args.dest != '-':
    parser.error("Path {d} does not exist".format(d=args.dest))

activator = os.path.join(os.path.dirname(argcomplete.__file__), 'bash_completion.d', 'python-argcomplete.sh')

if args.dest == '-':
    sys.stdout.write(open(activator).read())
else:
    dest = os.path.join(args.dest, "python-argcomplete.sh")
    sys.stdout.write("Installing bash completion script " + dest + "\n")
    try:
        shutil.copy(activator, dest)
    except Exception as e:
        err = str(e)
        if args.dest == dest_opt.default:
            err += "\nPlease try --user to install into a user directory, or --dest to specify the bash completion modules directory"
        parser.error(err)
