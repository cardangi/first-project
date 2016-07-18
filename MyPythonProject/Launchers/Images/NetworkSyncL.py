# -*- coding: ISO-8859-1 -*-
__author__ = 'Xavier ROSSET'


# ===================
# Absolute import(s).
# ===================
import os
import os.path
import argparse
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


# =================
# Arguments parser.
# =================
parser = argparse.ArgumentParser()
subparsers = parser.add_subparsers(dest="subparser")
parser_1 = subparsers.add_parser("1")
parser_1.add_argument("-b", "--batch", action="store_true")
parser_2 = subparsers.add_parser("2")
parser_3 = subparsers.add_parser("3")
arguments = parser.parse_args()


# ===============
# Main algorithm.
# ===============
cmd = [r"c:\python34\python.exe", "-m", "Applications.Images.NetworkSync", arguments.subparser]
if arguments.subparser == "1":
    if arguments.batch:
        cmd.append("-b")
with chgcurdir(r"G:\Documents\MyPythonProject"):
    subprocess.call(cmd)
