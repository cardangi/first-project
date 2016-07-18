# -*- coding: ISO-8859-1 -*-
__author__ = 'Xavier ROSSET'


# =================
# Absolute imports.
# =================
from jinja2 import Environment, FileSystemLoader
from datetime import datetime
from subprocess import run
from pytz import timezone
import itertools
import argparse
import sys
import os
import re


# =================
# Relative imports.
# =================
from . import shared


# ==========
# Functions.
# ==========
def pprint(t=None):
    run("CLS", shell=True)
    if t:
        print(t)


def validargument(t):
    rex = re.compile(r"^\d{10}$")
    if not rex.match(t):
        raise argparse.ArgumentTypeError('"{0}" is not a valid argument'.format(t))
    return int(t)


# =================
# Arguments parser.
# =================
parser = argparse.ArgumentParser()
parser.add_argument("start", help="Start epoch", type=validargument)
parser.add_argument("end", help="End epoch", type=validargument)
parser.add_argument("zone", help="Time zone")


# ======================
# Jinja2 environment(s).
# ======================
environment = Environment(loader=FileSystemLoader(os.path.join(os.path.expandvars("%_PYTHONPROJECT%"), "Applications", "Templates"), encoding=shared.DFTENCODING), trim_blocks=True, lstrip_blocks=True)


# ==========================
# Jinja2 global variable(s).
# ==========================
environment.globals["now"] = shared.now()
environment.globals["copyright"] = shared.COPYRIGHT


# ========================
# Jinja2 custom filter(s).
# ========================
environment.filters["ljustify"] = shared.ljustify
environment.filters["repeatelement"] = shared.repeatelement


# ===================
# Jinja2 template(s).
# ===================
template = environment.get_template("T3")


# ==========
# Constants.
# ==========
TABSIZE, EXIT, ZONES = 10, {"N": shared.BACK, "Y": shared.EXIT}, ["US/Pacific", "US/Eastern", "Indian/Mayotte", "Asia/Tokyo", "Australia/Sydney"]


# ================
# Initializations.
# ================
choice, status, arguments = "", 99, parser.parse_args()


# ===============
# Main algorithm.
# ===============

#  1. Configure headers.
headers = [zone for zone in ZONES]
headers.insert(2, arguments.zone)
headers.insert(0, "UTC")
headers.insert(0, "Timestamp")

#  2. Configure displayed zones.
zones = [zone for zone in ZONES]
zones.insert(2, arguments.zone)

#  3. Process arguments.
if arguments.start <= arguments.end:

    #  3a. Configure template layout.
    keys = [str(i).zfill(2) for i in range(1, len(headers) + 1)]
    lengths = list(itertools.repeat(30, len(headers) - 1))
    lengths.insert(0, 12)

    #  3b. Get epoch human representation.
    epoch = list(range(arguments.start, arguments.end + 1))
    epochlist = [[i for i in shared.getdatetime(arguments.start, zone, arguments.end)] for zone in zones]
    epochlist = [[item[i] for item in epochlist] for i in range(0, arguments.end - arguments.start + 1)]
    for i in range(0, len(epoch)):
        epochlist[i].insert(0, epoch[i])
        epochlist[i].insert(1, shared.dateformat(timezone("UTC").localize(datetime.utcfromtimestamp(epoch[i])), shared.TEMPLATE3))
    tmpl = template.render(d1=dict(zip(keys, headers)), d2=dict(zip(keys, lengths)), args=epochlist)

    #  3c. Display results.
    while True:
        pprint(t=tmpl)
        choice = input("{0}  Would you like to exit program [Y/N]? ".format("".join(list(itertools.repeat("\n", 2)))))
        if choice.upper() in shared.ACCEPTEDANSWERS:
            break
    status = EXIT[choice.upper()]


# ===============
# Exit algorithm.
# ===============
sys.exit(status)
