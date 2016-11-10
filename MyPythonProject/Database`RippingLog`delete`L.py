# -*- coding: ISO-8859-1 -*-
from contextlib import contextmanager, ExitStack
import subprocess
import json
import sys
import os

__author__ = 'Xavier ROSSET'


# ==========
# Constants.
# ==========
JSON = os.path.join(os.path.expandvars("%TEMP%"), "arguments.json")


# ================
# Initializations.
# ================
numbers, status = None, 100


# =========
# Commands.
# =========
cmd1 = ["python", "-m", "Applications.Database.RippingLog.delete`I"]  # "I" means Interface! "L" means Launcher!
cmd2 = ["python", "-m", "Applications.CDRipper.AudioCD`RippingLog", "delete"]


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
with chgcurdir(os.path.expandvars("%_PYTHONPROJECT%")):
    task1 = subprocess.run(cmd1)
    status = task1.returncode
    if not task1.returncode:
        if os.path.exists(JSON):
            stack = ExitStack()
            stack.callback(os.remove, JSON)
            with stack:
                with open(JSON) as fp:
                    numbers = json.load(fp)
    if numbers:
        cmd2.extend(numbers)
        task2 = subprocess.run(cmd2)
        status = task2.returncode
sys.exit(status)
