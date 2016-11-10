# -*- coding: ISO-8859-1 -*-
import os
import json
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


# ==========
# Constants.
# ==========
INPUT, PYTHON = os.path.join(os.path.expandvars("%TEMP%"), "arguments.json"), r"C:\Program Files (x86)\Python35-32\python.exe"


# ================
# Initializations.
# ================
dftargs, view1 = [PYTHON, "-m", "Applications.CDRipper.AudioCD`RippingLog", "update"], False


# ===============
# Main algorithm.
# ===============
with chgcurdir(os.path.expandvars("%_PYTHONPROJECT%")):

    #     -----------------
    #  1. Enter new values.
    #     -----------------
    process1 = subprocess.run([PYTHON, "-m", "Applications.Database.RippingLog.dbRippingLog"])

    #     ----------------
    #  2. Update database.
    #     ----------------
    #     Tous les éléments de la liste "args" doivent être définis en alphanumérique !
    if not process1.returncode:
        if os.path.exists(INPUT):
            with open(INPUT, encoding="ISO-8859-1") as fr:
                for argument in json.load(fr):
                    if len(argument) >= 2:
                        args = [item for item in dftargs]
                        args.append("{0}".format(argument[0]))
                        for key, value in argument[1].items():
                            args.append("--{0}".format(key))
                            args.append("{0}".format(value))
                        process2 = subprocess.run(args)
                        if not process2.returncode:
                            view1 = True


# =================
# Update HTML view.
# =================
if view1:
    process3 = subprocess.run([PYTHON, r"G:\Computing\MyPythonProject\Database`HTMLView`L.py", "RippingLog"])
    with chgcurdir(os.path.expandvars("%_PYTHONPROJECT%")):
        process4 = subprocess.run([PYTHON, "-m", "Applications.Database.RippingLog.View2"])
