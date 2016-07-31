# -*- coding: ISO-8859-1 -*-
__author__ = 'Xavier ROSSET'


# =================
# Absolute imports.
# =================
from jinja2 import Environment, FileSystemLoader
from subprocess import run
import json
import sys
import os
import re


# =================
# Relative imports.
# =================
from .. import shared


# ======================
# Jinja2 environment(s).
# ======================
environment = Environment(loader=FileSystemLoader(os.path.join(os.path.expandvars("%_PYTHONPROJECT%"), "Applications", "Tasks", "Templates"), encoding=shared.DFTENCODING),
                          trim_blocks=True,
                          lstrip_blocks=True,
                          keep_trailing_newline=True)


# ===================
# Jinja2 template(s).
# ===================
template = environment.get_template("T1")


# ==========
# Functions.
# ==========
def pprint(t):
    run("CLS", shell=True)
    if t:
        print(t)


# ====================
# Regular expressions.
# ====================
rex1 = re.compile(r"^\d\d?$")


# ==========
# Constants.
# ==========
TASKS = os.path.join(os.path.expandvars("%_PYTHONPROJECT%"), "Applications", "Tasks", "Tasks.json")
CODES = os.path.join(os.path.expandvars("%_PYTHONPROJECT%"), "Applications", "Tasks", "ReturnCodes.json")


# ================
# Initializations.
# ================
choice, status = 99, 100


# ===============
# Main algorithm.
# ===============

#  1. Load available tasks.
with open(TASKS) as fp:
    tasks = [item for item in json.load(fp)][0]

#  2. Load available return codes.
with open(CODES) as fp:
    codes = [item for item in json.load(fp)][0]

#  3. Grab choice.
if all([tasks, codes]):
    o = template.render(tasks=dict(zip([str(i) for i in range(1, len(tasks) + 1)], tasks)))
    while True:
        pprint(t=o)
        choice = input("\t\tPlease enter task: ".expandtabs(4))
        if choice:
            if not rex1.match(choice):
                continue
            if choice not in codes and choice != "99":
                continue
            break
    status = int(choice)
    if status != 99:
        status = codes[choice]


# ===============
# Exit algorithm.
# ===============
sys.exit(status)
