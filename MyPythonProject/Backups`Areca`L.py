# -*- coding: ISO-8859-1 -*-
__author__ = 'Xavier ROSSET'


# =================
# Absolute imports.
# =================
import os
import sys
import json
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


def validworkspace(s):
    if s not in ["documents", "miscellaneous", "music", "pictures", "videos"]:
        raise argparse.ArgumentTypeError('"{0}" is not a valid workspace'.format(s))
    return s


# =================
# Arguments parser.
# =================
parser = argparse.ArgumentParser()
parser.add_argument("workspace", type=validworkspace)
parser.add_argument("--target", nargs="*")
parser.add_argument("--full", action="store_true")
parser.add_argument("--check", action="store_true")
parser.add_argument("--debug", action="store_true")


# ==========
# Constants.
# ==========
KEYS, PYTHON, CFGFILE = ["description", "target", "workspace"], os.path.expandvars("%_PYTHONPROJECT%"), os.path.join(os.path.expandvars("%_PYTHONPROJECT%"), "Applications", "Backups", "Areca.json")


# ================
# Initializations.
# ================
status, arguments, args = 99, parser.parse_args(), [r"C:\Program Files (x86)\Python35-32\python.exe", "-m", "Applications.Backups.Areca"]


# ===============
# Main algorithm.
# ===============


#     -----------------------------
#  1. Reference backups repository.
#     -----------------------------
with open(CFGFILE, encoding="UTF_8") as fp:
    targets = [(d["workspace"], d["target"]) for d in json.load(fp) if sorted([key.lower() for key in d.keys()]) == sorted(KEYS)]


#     -----------------
#  2. Required backups.
#     -----------------
target = [(arguments.workspace, target) for workspace, target in targets if arguments.workspace == workspace]
if arguments.target:
    target = [(arguments.workspace, target) for target in arguments.target]


#     ---------------------------
#  3. Run backups.
#     Must match with repository!
#     ---------------------------
args.append(arguments.workspace)
for t in target:
    if t in targets:
        args.append(t[1])
if len(args) >= 5:
    if arguments.full:
        args.append("--full")
    if arguments.check:
        args.append("--check")
    if arguments.debug:
        args.append("--debug")
    with chgcurdir(PYTHON):
        process = subprocess.run(args)
        status = process.returncode


# ===============
# Exit algorithm.
# ===============
sys.exit(status)
