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
        process1 = subprocess.run([PYTHON, "-m", "Applications.convertUnixEpoch1"])
        if process1.returncode:
            returncode = process1.returncode
            break
        if os.path.exists(INFILE):
            with open(INFILE, encoding="ISO-8859-1") as fp:
                for arguments in json.load(fp):
                    if len(arguments) >= 3:
                        command = [arguments[i] for i in range(0, 3)]
                        command.insert(0, "Applications.convertUnixEpoch2")
                        command.insert(0, "-m")
                        command.insert(0, PYTHON)
                        process2 = subprocess.run(command)
                        if process2.returncode in [11, 99]:
                            returncode = process2.returncode
                            break
                if returncode in [11, 99]:
                    break


# ===============
# Exit algorithm.
# ===============
sys.exit(returncode)
