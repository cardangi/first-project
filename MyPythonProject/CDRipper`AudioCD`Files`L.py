# -*- coding: ISO-8859-1 -*-
import os
import argparse
import subprocess
from contextlib import contextmanager

__author__ = 'Xavier ROSSET'


# =================
# Arguments parser.
# =================
parser = argparse.ArgumentParser()
parser.add_argument("ifile")
parser.add_argument("ofile")


# ================
# Initializations.
# ================
arguments = parser.parse_args()


# ==========
# Functions.
# ==========
@contextmanager
def chgcurdir(d):
    wcdir = os.getcwd()
    os.chdir(d)
    yield
    os.chdir(wcdir)


# ===============
# Main algorithm.
# ===============
cmd = [r"C:\Program Files (x86)\Python35-32\python.exe", "-m", "Applications.CDRipper.AudioCDFiles", arguments.ifile, arguments.ofile]
with chgcurdir(os.path.expandvars("%_PYTHONPROJECT%")):
    subprocess.run(cmd)
