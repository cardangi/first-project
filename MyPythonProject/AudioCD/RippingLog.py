# -*- coding: ISO-8859-1 -*-
import sys
import argparse
from Applications.Database.RippedCD.shared import insertfromfile

__author__ = 'Xavier ROSSET'


# =================
# Arguments parser.
# =================
parser = argparse.ArgumentParser()
parser.add_argument("tracks", type=argparse.FileType(mode="r"))


# ================
# Initializations.
# ================
arguments = parser.parse_args()


# ===============
# Main algorithm.
# ===============
status = insertfromfile(arguments.tracks)


# ===============
# Exit algorithm.
# ===============
sys.exit(status)
