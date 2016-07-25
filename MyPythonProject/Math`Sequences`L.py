# -*- coding: ISO-8859-1 -*-
import os
import argparse
import subprocess
from contextlib import contextmanager

__author__ = 'Xavier ROSSET'


# ==========
# Functions.
# ==========
@contextmanager
def chgcurdir(d):
    wcdir = os.getcwd()
    os.chdir(d)
    yield
    os.chdir(wcdir)


# =================
# Arguments parser.
# =================
parser = argparse.ArgumentParser()
parser.add_argument("type", help="type of the sequence: arithmetic or geometric.")
arguments = parser.parse_args()


# ===============
# Main algorithm.
# ===============
with chgcurdir(os.path.expandvars("%_pythonproject%")):
    while True:
        process = subprocess.run([r"C:\Program Files (x86)\Python35-32\python.exe", "-m", "Applications.Math.Sequences", arguments.type])
        if process.returncode != 12:
            break
