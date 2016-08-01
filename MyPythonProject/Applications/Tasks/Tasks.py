# -*- coding: ISO-8859-1 -*-
from jinja2 import Environment, FileSystemLoader
from subprocess import run
import json
import sys
import os
import re
from .. import shared

__author__ = 'Xavier ROSSET'


# ==========
# Constants.
# ==========
TASKS = os.path.join(os.path.expandvars("%_PYTHONPROJECT%"), "Applications", "Tasks", "Tasks.json")


# ==========
# Functions.
# ==========
def pprint(t):
    run("CLS", shell=True)
    if t:
        print(t)


def inserttabulations(s, l=56, tab=4):
    x = (l - len(s))//tab
    if (l - len(s)) % tab:
        x += 1
    return "\t"*x


def expandtabulations(s, tab=4):
    return s.expandtabs(tab)


# ===================
# Jinja2 environment.
# ===================
environment = Environment(loader=FileSystemLoader(os.path.join(os.path.expandvars("%_PYTHONPROJECT%"), "Applications", "Tasks", "Templates"), encoding=shared.DFTENCODING),
                          trim_blocks=True,
                          lstrip_blocks=True,
                          keep_trailing_newline=True)


# ======================
# Jinja2 custom filters.
# ======================
environment.filters["inserttabulations"] = inserttabulations
environment.filters["expandtabulations"] = expandtabulations


# ================
# Jinja2 template.
# ===============
template = environment.get_template("T1")


# ====================
# Regular expressions.
# ====================
rex1 = re.compile(r"^\d\d?$")


# ================
# Initializations.
# ================
choice, returncode = 99, 100


# ===============
# Main algorithm.
# ===============

# 1. Load both tasks and return codes.
with open(TASKS) as fp:
    data = json.load(fp)
    tasks = [title for title, number, code in [tuple(item) for item in data]]
    codes = dict([(str(number), code) for title, number, code in [tuple(item) for item in data]])

# 2. Choose task.
if all([tasks, codes]):
    o = template.render(tasks=tasks)
    while True:
        pprint(t=o)
        choice = input("\t\tPlease enter task: ".expandtabs(4))
        if choice:
            if not rex1.match(choice):
                continue
            if choice not in codes:
                continue
            break
    returncode = codes[choice]


# ===============
# Exit algorithm.
# ===============
sys.exit(returncode)
