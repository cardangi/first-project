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
parser.add_argument("directory", help="browsed directory")
parser.add_argument("archive", help="archive name")
parser.add_argument("destination", help="archive destination")
parser.add_argument("-e", "--extensions", help="archived extension(s)", nargs="*")
parser.add_argument("-x", "--exclude", help="excluded extension(s)", nargs="*")
parser.add_argument("-c", "--encrypt", help="encrypt file(s)", action="store_true")
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


# ==================
# Initialization(s).
# ==================
curdir = r"G:\Documents\MyPythonProject"


# ===============
# Main algorithm.
# ===============
cmd = ["python", "-m", "Applications.Tasks.ZipFile", arguments.directory, arguments.archive, arguments.destination]
if arguments.extensions:
    cmd.append("--extensions")
    for i in arguments.extensions:
        cmd.append(i)
if arguments.exclude:
    cmd.append("--exclude")
    for i in arguments.exclude:
        cmd.append(i)
if arguments.encrypt:
    cmd.append("--encrypt")
if arguments.debug:
    cmd.append("--debug")
with chgcurdir(curdir):
    subprocess.call(cmd)
