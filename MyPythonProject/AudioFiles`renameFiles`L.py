# -*- coding: ISO-8859-1 -*-
__author__ = 'Xavier ROSSET'


# ===================
# Absolute import(s).
# ===================
import os
import json
import subprocess
from contextlib import contextmanager


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
INFILE, PYTHON = os.path.join(os.path.expandvars("%TEMP%"), "arguments.json"), r"C:\Program Files (x86)\Python35-32\python.exe"


# ===============
# Main algorithm.
# ===============
with chgcurdir(os.path.expandvars("%_PYTHONPROJECT%")):
    while True:
        process1 = subprocess.run([PYTHON, "-m", "Applications.AudioFiles.renameFiles1"])
        if not process1.returncode:
            if os.path.exists(INFILE):
                with open(INFILE, encoding="ISO-8859-1") as fp:
                    for argument in json.load(fp):
                        args = [PYTHON, "-m", "Applications.AudioFiles.renameFiles2", argument[0]]
                        for extension in argument[1]:
                            args.append(extension)
                        if len(args) > 4:
                            args.insert(4, "--extensions")
                        process2 = subprocess.run(args)
                        if process2.returncode == 12:
                            continue
                        break
            break
        break
