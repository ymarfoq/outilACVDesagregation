# -*- coding: UTF-8 -*-
from __future__ import print_function, division, absolute_import

import sys
import argparse
import os
import subprocess


def make_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('--annotate',  help='Annotate source',
                        action='store_true')
    parser.add_argument('--dump-llvm', action="store_true",
                        help='Print generated llvm assembly')
    parser.add_argument('--dump-optimized', action='store_true',
                        help='Dump the optimized llvm assembly')
    parser.add_argument('--dump-assembly', action='store_true',
                        help='Dump the LLVM generated assembly')
    parser.add_argument('--dump-cfg', action="store_true",
                        help='[Deprecated] Dump the control flow graph')
    parser.add_argument('--dump-ast', action="store_true",
                        help='[Deprecated] Dump the AST')
    parser.add_argument('--fancy', action='store_true',
                        help='Try to output fancy files (.dot or .html)')
    parser.add_argument('filename', help='Python source filename')
    return parser

if __name__ == "__main__":
    parser = make_parser()
    args = parser.parse_args()

    if args.dump_cfg:
        print("CFG dump is removed.")
        sys.exit(1)
    if args.dump_ast:
        print("AST dump is removed.  Numba no longer depends on AST.")
        sys.exit(1)
    if args.fancy:
        print("Unavailable in this release.")

    os.environ['NUMBA_DUMP_ANNOTATION'] = str(int(args.annotate))
    os.environ['NUMBA_DUMP_LLVM'] = str(int(args.dump_llvm))
    os.environ['NUMBA_DUMP_OPTIMIZED'] = str(int(args.dump_optimized))
    os.environ['NUMBA_DUMP_ASSEMBLY'] = str(int(args.dump_assembly))

    cmd = [sys.executable, args.filename]
    subprocess.call(cmd)

