# -*- coding: ISO-8859-1 -*-
import os
import sys
import json
import subprocess
from contextlib import contextmanager

__author__ = 'Xavier ROSSET'


# ==========
# Constants.
# ==========
PYTHON, INFILE = r"C:\Program Files (x86)\Python35-32\python.exe", os.path.join(os.path.expandvars("%TEMP%"), "arguments")


# ================
# Initializations.
# ================
returncode = 999


# =========
# Commands.
# =========
cmd1 = [PYTHON, "-m", "Applications.convertUnixEpoch1"]
cmd2 = [PYTHON, "-m", "Applications.convertUnixEpoch2"]


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
with chgcurdir(os.path.expandvars("%_PYTHONPROJECT%")):
    while True:
        task1 = subprocess.run(cmd1)
        if task1.returncode:
            returncode = task1.returncode
            break
        if os.path.exists(INFILE):
            with open(INFILE, encoding="ISO-8859-1") as fp:
                cmd = list(cmd2)
                cmd.extend(json.load(fp))
                task2 = subprocess.run(cmd)
                if task2.returncode in [11, 99]:
                    returncode = task2.returncode
                    break


# ===============
# Exit algorithm.
# ===============
sys.exit(returncode)
