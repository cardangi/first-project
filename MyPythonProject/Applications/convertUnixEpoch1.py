# -*- coding: ISO-8859-1 -*-
import os
import re
import sys
import json
import locale
from subprocess import run
from functools import wraps
from datetime import datetime
from collections import namedtuple
from pytz import all_timezones, timezone
from jinja2 import Environment, FileSystemLoader
from . import shared

__author__ = 'Xavier ROSSET'


# ==========================
# Define French environment.
# ==========================
locale.setlocale(locale.LC_ALL, "")


# ==========
# Constants.
# ==========
OUTFILE, TABSIZE = os.path.join(os.path.expandvars("%TEMP%"), "arguments"), 10


# ==========
# Functions.
# ==========
def renderheader(func):

    @wraps(func)
    def wrapper(t):
        func()
        return t

    return wrapper


@renderheader
def clearscreen():
    run("CLS", shell=True)


# ====================
# Regular expressions.
# ====================
regex = re.compile(r"^\d{10}$")


# ======================
# Jinja2 environment(s).
# ======================
environment = Environment(loader=FileSystemLoader(os.path.join(os.path.expandvars("%_PYTHONPROJECT%"), "Applications", "AudioFiles", "Templates"), encoding=shared.DFTENCODING), trim_blocks=True, lstrip_blocks=True)


# ==========================
# Jinja2 global variable(s).
# ==========================
environment.globals["now"] = shared.now()
environment.globals["copyright"] = shared.COPYRIGHT


# ========================
# Jinja2 custom filter(s).
# ========================
environment.filters["integertostring"] = shared.integertostring
environment.filters["repeatelement"] = shared.repeatelement
environment.filters["ljustify"] = shared.ljustify
environment.filters["rjustify"] = shared.rjustify


# ===================
# Jinja2 template(s).
# ===================
template = environment.get_template("T1")


# =================
# Initializations 1.
# =================
answer, status, zone = "", 99, shared.DFTTIMEZONE


# ==================
# Initializations 2.
# ==================
nt = namedtuple("nt", "maintitle step title")


# ===============
# Main algorithm.
# ===============
while True:

    header = shared.Header("convert unix epoch", ["Set start epoch.", "Set end epoch.", "Set time zone.", "Confirm arguments"])
    head = header()
    tmpl = template.render(header=nt(*head))

    #     ----------------
    #  1. Set start epoch.
    #     ----------------
    while True:
        print(clearscreen(t=tmpl))
        choice = input("\n\n\tPlease enter (not mandatory) start epoch: ".expandtabs(TABSIZE))
        if choice:
            if not regex.match(choice):
                tmpl = template.render(header=nt(*head), message=list(('"{0}" is not a valid epoch.'.format(choice),)))
                continue
            start = int(choice)
            break
        start = int(timezone("UTC").localize(datetime.utcnow()).timestamp())
        break
    end = start
    head = header()
    tmpl = template.render(header=nt(*head))

    #     --------------
    #  2. Set end epoch.
    #     --------------
    while True:
        print(clearscreen(t=tmpl))
        choice = input("\n\n\tPlease enter (not mandatory) end epoch: ".expandtabs(TABSIZE))
        if choice:
            if not regex.match(choice):
                tmpl = template.render(header=nt(*head), message=list(('"{0}" is not a valid epoch.'.format(choice),)))
                continue
            end = int(choice)
            if end < start:
                tmpl = template.render(header=nt(*head), message=list(("End epoch must be greater than {0}.".format(start),)))
                continue
            break
        break
    head = header()
    tmpl = template.render(header=nt(*head))

    #     --------------
    #  3. Set time zone.
    #     --------------
    while True:
        print(clearscreen(t=tmpl))
        choice = input("\n\n\tPlease enter (not mandatory) time zone: ".expandtabs(TABSIZE))
        if choice:
            if choice not in all_timezones:
                tmpl = template.render(header=nt(*head), message=list(('"{0}" is not a valid time zone.'.format(choice),)))
                continue
            zone = choice
            break
        break
    head = header()
    tmpl = template.render(header=nt(*head), message=list(("Start epoch\t: {0}.".format(start).expandtabs(4), "End epoch\t: {0}.".format(end).expandtabs(4))))

    #     -----------------------------------
    #  4. Display arguments for confirmation.
    #     -----------------------------------
    while True:
        print(clearscreen(t=tmpl))
        answer = input("\n\n\tWould you like to convert unix epoch from {0} to {1} [Y/N]? ".format(start, end).expandtabs(TABSIZE))
        if answer.upper() in shared.ACCEPTEDANSWERS:
            break
    if answer.upper() == "Y":
        with open(OUTFILE, mode=shared.WRITE, encoding=shared.DFTENCODING) as fp:
            json.dump([str(start), str(end), zone], fp, indent=4)
        status = 0
        break
    if answer.upper() == "N":
        while True:
            print(clearscreen(t=tmpl))
            answer = input("\n\n\tWould you like to exit program [Y/N]? ".expandtabs(TABSIZE))
            if answer.upper() in shared.ACCEPTEDANSWERS:
                break
        if answer.upper() == "Y":
            break


# =============
# Exit program.
# =============
sys.exit(status)
