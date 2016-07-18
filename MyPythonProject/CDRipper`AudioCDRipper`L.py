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
parser.add_argument("profile", help="rip profile")
parser.add_argument("-t", "--test", action="store_true")
parser.add_argument("-d", "--debug", action="store_true")
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
cmd = [r"C:\Program Files (x86)\Python35-32\python.exe", "-m", "Applications.CDRipper.AudioCDRipper", arguments.input, arguments.profile]
if arguments.test:
    cmd.append("--test")
if arguments.debug:
    cmd.append("--debug")
with chgcurdir(r"G:\Computing\MyPythonProject"):
    subprocess.run(cmd)
