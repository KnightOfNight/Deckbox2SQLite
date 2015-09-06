#!/usr/bin/env python


import argparse
import sys


version = sys.hexversion
if version < 0x02070000:
    sys.stderr.write('python 2.7 or higher required\n')
    sys.exit(-1)


parser = argparse.ArgumentParser(description = 'Create an SQLite database from a Deckbox export.', formatter_class = argparse.ArgumentDefaultsHelpFormatter)
args = parser.parse_args()


