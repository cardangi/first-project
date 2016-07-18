# -*- coding: ISO-8859-1 -*-
__author__ = 'Xavier ROSSET'


# =================
# Absolute imports.
# =================
from jinja2 import Environment, FileSystemLoader
from subprocess import run
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
NUMBER = 22


# ================
# Initializations.
# ================
task = 99


# ===============
# Main algorithm.
# ===============
o = template.render()
while True:
    pprint(t=o)
    task = input("\t\tPlease enter task: ".expandtabs(4))
    if task:
        if not rex1.match(task):
            continue
        task = int(task)
        if task not in range(1, NUMBER+1) and task != 99:
            continue
        break
sys.exit(task)
