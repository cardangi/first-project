# -*- coding: ISO-8859-1 -*-
import os
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


# ===============
# Main algorithm.
# ===============
with chgcurdir(os.path.expandvars("%_PYTHONPROJECT%")):
    while True:
        process = subprocess.run([r"C:\Program Files (x86)\Python35-32\python.exe", "-m", "Applications.Database.IHM"])
        if process.returncode != 12:
            break
