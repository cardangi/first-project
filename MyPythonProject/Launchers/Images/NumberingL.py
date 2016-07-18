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
parser.add_argument("year")
parser.add_argument("-t", "--template", nargs="?", default="%cy%{m}_%{n}")
parser.add_argument("-s", "--start", nargs="?", type=int, default=1)
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
cmd = [r"c:\python34\python.exe", "-m", "Applications.Images.Numbering", arguments.year]
if arguments.template:
    cmd.append("--template")
    cmd.append(arguments.template)
if arguments.start:
    cmd.append("--start")
    cmd.append(str(arguments.start))
with chgcurdir(r"G:\Documents\MyPythonProject"):
    subprocess.call(cmd)
