# -*- coding: ISO-8859-1 -*-
__author__ = 'Xavier ROSSET'


# =================
# Absolute imports.
# =================
import os
import re
import sys
import json
import locale
from subprocess import run
from datetime import datetime
from pytz import all_timezones, timezone
from jinja2 import Environment, FileSystemLoader


# =================
# Relative imports.
# =================
from . import shared


# ==========================
# Define French environment.
# ==========================
locale.setlocale(locale.LC_ALL, "")


# ==========
# Constants.
# ==========
HEADER, TITLES, OUTFILE, TABSIZE = "convert unix epoch", \
                                   ["Set start epoch.", "Set end epoch.", "Set time zone.", "Confirm arguments"], \
                                   os.path.join(os.path.expandvars("%TEMP%"), "arguments"), \
                                   10


# ==========
# Functions.
# ==========
def pprint(t=None):
    run("CLS", shell=True)
    if t:
        print(t)


# ========
# Classes.
# ========
class Header:
    pass


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
answer, step, status, zone, titles = "", 0, 99, shared.DFTTIMEZONE, dict(zip([str(i) for i in range(1, len(TITLES) + 1)], TITLES))


# ==================
# Initializations 2.
# ==================
header = Header()
header.main = HEADER


# ===============
# Main algorithm.
# ===============
while True:

    step += 1
    header.step = step
    header.title = titles[str(step)]
    tmpl = template.render(header=header)

    #     ----------------
    #  1. Set start epoch.
    #     ----------------
    while True:
        pprint(t=tmpl)
        choice = input("\n\n\tPlease enter (not mandatory) start epoch: ".expandtabs(TABSIZE))
        if choice:
            if not regex.match(choice):
                tmpl = template.render(header=header, message=list(('"{0}" is not a valid epoch.'.format(choice),)))
                continue
            start = int(choice)
            break
        start = int(timezone("UTC").localize(datetime.utcnow()).timestamp())
        break
    end = start
    step += 1
    header.step = step
    header.title = titles[str(step)]
    tmpl = template.render(header=header)

    #     --------------
    #  2. Set end epoch.
    #     --------------
    while True:
        pprint(t=tmpl)
        choice = input("\n\n\tPlease enter (not mandatory) end epoch: ".expandtabs(TABSIZE))
        if choice:
            if not regex.match(choice):
                tmpl = template.render(header=header, message=list(('"{0}" is not a valid epoch.'.format(choice),)))
                continue
            end = int(choice)
            if end < start:
                tmpl = template.render(header=header, message=list(("End epoch must be greater than {0}.".format(start),)))
                continue
            break
        break
    step += 1
    header.step = step
    header.title = titles[str(step)]
    tmpl = template.render(header=header)

    #     --------------
    #  3. Set time zone.
    #     --------------
    while True:
        pprint(t=tmpl)
        choice = input("\n\n\tPlease enter (not mandatory) time zone: ".expandtabs(TABSIZE))
        if choice:
            if choice not in all_timezones:
                tmpl = template.render(header=header, message=list(('"{0}" is not a valid time zone.'.format(choice),)))
                continue
            zone = choice
            break
        break
    step += 1
    header.step = step
    header.title = titles[str(step)]
    tmpl = template.render(header=header, message=list(("Start epoch\t: {0}.".format(start).expandtabs(4), "End epoch\t: {0}.".format(end).expandtabs(4))))

    #     -----------------------------------
    #  4. Display arguments for confirmation.
    #     -----------------------------------
    while True:
        pprint(t=tmpl)
        answer = input("\n\n\tWould you like to convert unix epoch from {0} to {1} [Y/N]? ".format(start, end).expandtabs(TABSIZE))
        if answer.upper() in shared.ACCEPTEDANSWERS:
            break
    if answer.upper() == "Y":
        with open(OUTFILE, mode=shared.WRITE, encoding=shared.DFTENCODING) as fp:
            json.dump([(str(start), str(end), zone)], fp, indent=4)
        status = 0
        break
    if answer.upper() == "N":
        while True:
            pprint(t=tmpl)
            answer = input("\n\n\tWould you like to exit program [Y/N]? ".expandtabs(TABSIZE))
            if answer.upper() in shared.ACCEPTEDANSWERS:
                break
        if answer.upper() == "Y":
            break
        if answer.upper() == "N":
            step = 0


# =============
# Exit program.
# =============
sys.exit(status)
