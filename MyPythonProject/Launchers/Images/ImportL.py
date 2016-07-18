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
parser.add_argument("-s", "--select")
parser.add_argument("-t", "--template", nargs="?", default="%cy%{m}_%{n}")
subparser = parser.add_subparsers(dest="input")
parser_dir = subparser.add_parser("dir")
parser_dir.add_argument("dir")
parser_fil = subparser.add_parser("fil")
parser_fil.add_argument("fil")
arguments = parser.parse_args()


# ==================
# Initialization(s).
# ==================
curdir = r"G:\Documents\MyPythonProject"


# ===============
# Main algorithm.
# ===============
cmd = [r"c:\python34\python.exe", "-m", "Applications.Images.Import"]
if arguments.select:
    cmd.append("--select")
    cmd.append(arguments.select)
if arguments.template:
    cmd.append("--template")
    cmd.append(arguments.template)
cmd.append(arguments.input)
if arguments.input == "dir":
    cmd.append(arguments.dir)
if arguments.input == "fil":
    cmd.append(arguments.fil)
with chgcurdir(curdir):
    subprocess.call(cmd)
