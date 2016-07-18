# -*- coding: ISO-8859-1 -*-
__author__ = 'Xavier ROSSET'


# ===================
# Absolute import(s).
# ===================
import os
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


# ===============
# Main algorithm.
# ===============
with chgcurdir(r"G:\Documents\MyPythonProject"):
    subprocess.call([r"c:\python34\python.exe", "-m", "Applications.CDRipper.NetworkSync"])
