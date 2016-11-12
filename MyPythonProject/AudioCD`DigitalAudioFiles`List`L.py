# -*- coding: ISO-8859-1 -*-
import os
import argparse
import subprocess
from contextlib import contextmanager

__author__ = 'Xavier ROSSET'


# ==========
# Functions.
# ==========
def isvaliddirectory(d):
    if not os.path.isdir(d):
        raise argparse.ArgumentTypeError('"{0}" is not a valid directory'.format(d))
    if not os.access(d, os.R_OK):
        raise argparse.ArgumentTypeError('"{0}" is not a readable directory'.format(d))
    return d


# =================
# Arguments parser.
# =================
parser = argparse.ArgumentParser()
parser.add_argument("directory", help="mandatory directory to walk through", type=isvaliddirectory)
parser.add_argument("-e", "--ext", dest="extensions", help="one or more extension(s) to filter out", nargs="*")
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
cmd = ["python", os.path.join("AudioCD", "DigitalAudioFiles`List.py"), arguments.directory]
if arguments.extensions:
    cmd.extend(arguments.extensions)
with chgcurdir(os.path.expandvars("%_PYTHONPROJECT%")):
    subprocess.run(cmd)
