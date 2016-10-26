# -*- coding: ISO-8859-1 -*-
import os
import sys
import json
import argparse
import tempfile
import operator
import subprocess
from contextlib import contextmanager

__author__ = 'Xavier ROSSET'


# ==========
# Functions.
# ==========
def validprofile(p):
    if p not in ["default", "bootlegs", "pjbootlegs"]:
        raise argparse.ArgumentTypeError('"{0}" is not a valid profile'.format(p))
    return p


# =================
# Arguments parser.
# =================
parser = argparse.ArgumentParser()
parser.add_argument("profile", help="rip profile", type=validprofile)
parser.add_argument("-t", "--test", action="store_true")
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


# ==========
# Constants.
# ==========
CURDIR = r"G:\Computing\MyPythonProject"


# ================
# Initializations.
# ================
returncodes, dftcmd = [], [r"C:\Program Files (x86)\Python35-32\python.exe", r"G:\Computing\MyPythonProject\CDRipper`AudioCDRipper`L.py"]


# ===============
# Main algorithm.
# ===============
with tempfile.TemporaryDirectory() as tmpdir:
    tagsfile = os.path.join(tmpdir, "tags.txt")
    cmd = [item for item in dftcmd]
    cmd.append(tagsfile)
    cmd.append(arguments.profile)
    with open(os.path.join(os.path.expandvars("%_COMPUTING%"), "AudioCDRipperTest.json")) as fp:
        for element in json.load(fp):  # "element" est un dictionnaire.
            if arguments.profile in element:
                for key in element[arguments.profile]:  # "key" est un dictionnaire.
                    with open(tagsfile, "w", encoding="UTF_16LE") as fw:
                        for subkey in element[arguments.profile][key]:
                            fw.write("{}={}\n".format(subkey, element[arguments.profile][key][subkey]))
                    with chgcurdir(CURDIR):
                        if arguments.test:
                            cmd.append("--test")
                        process = subprocess.run(cmd)
                        returncodes.append(process.returncode)


# ===============
# Exit algorithm.
# ===============
if not returncodes:
    sys.exit(99)
if all([not(operator.eq(i, 0)) for i in returncodes]):
    sys.exit(98)
if any([not(operator.eq(i, 0)) for i in returncodes]):
    sys.exit(97)
sys.exit(0)
