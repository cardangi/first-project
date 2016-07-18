# -*- coding: ISO-8859-1 -*-
__author__ = 'Xavier ROSSET'


# =================
# Absolute imports.
# =================
import os
import sys
import json
import argparse
import operator
from subprocess import run, PIPE
from os.path import expandvars, join
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
parser.add_argument("table", nargs="+")


# ==========
# Constants.
# ==========
KEYS, PYTHON, CFGFILE = ["output", "script", "table"], expandvars("%_PYTHONPROJECT%"), join(expandvars("%_PYTHONPROJECT%"), "Applications", "Database", "HTML.json")


# ================
# Initializations.
# ================
returncode, args, arguments = [], [r"C:\Program Files (x86)\Python35-32\python.exe", "-m"], parser.parse_args()


# ===============
# Main algorithm.
# ===============
with open(CFGFILE, encoding="ISO-8859-1") as fp:

    for configuration in json.load(fp):

        if sorted([key for key in iter(configuration)]) == sorted(KEYS):

            if configuration["table"].lower() in [table.lower() for table in arguments.table]:
                args.append(configuration["script"])
                with chgcurdir(PYTHON):
                    process = run(args, stdout=PIPE, universal_newlines=True)
                    returncode.append(process.returncode)
                    if not process.returncode:
                        with open(configuration["output"], mode="w", encoding="UTF_8") as fw:
                            for line in process.stdout.splitlines():
                                fw.write("%s\n" % (line,))


# ===============
# Exit algorithm.
# ===============
if not returncode:
    sys.exit(99)
if all(not operator.eq(i, 0) for i in returncode):
    sys.exit(99)
if any(operator.eq(i, 0) for i in returncode):
    sys.exit(0)
