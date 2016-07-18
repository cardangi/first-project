# -*- coding: ISO-8859-1 -*-
__author__ = 'Xavier ROSSET'


# ===================
# Absolute import(s).
# ===================
import os
import argparse
import subprocess
from contextlib import contextmanager


# =================
# Arguments parser.
# =================
parser = argparse.ArgumentParser()
parser.add_argument("input", help="tags file")
parser.add_argument("profile", help="tags profile")
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
with chgcurdir(r"G:\Documents\MyPythonProject"):
    subprocess.call([r"c:\python34\python.exe", "-m", "Applications.CDRipper.AudioConverter", arguments.input, arguments.profile])
