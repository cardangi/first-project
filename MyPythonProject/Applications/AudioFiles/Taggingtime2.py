# -*- coding: ISO-8859-1 -*-
__author__ = 'Xavier ROSSET'


# =================
# Absolute imports.
# =================
from datetime import datetime
from itertools import repeat
from pytz import timezone
import argparse
import re


# =================
# Relative imports.
# =================
from .. import shared


# ==========
# Functions.
# ==========
def validnumber(i):
    regex = re.compile(r"^\d(\d{1,2})?$")
    if not regex.match(i):
        raise argparse.ArgumentTypeError('"{0}" is not a valid number of file(s).'.format(i))
    if int(i) == 0:
        raise argparse.ArgumentTypeError("0 is not a valid number of file(s).")
    return int(i)


# =================
# Arguments parser.
# =================
parser = argparse.ArgumentParser()
parser.add_argument("number", help="Number of file(s)", type=validnumber)


# ================
# Initializations.
# ================
arguments = parser.parse_args()


# ===============
# Main algorithm.
# ===============
print("".join(list(repeat("{0}\n".format(shared.dateformat(datetime.now(tz=timezone(shared.DFTTIMEZONE)), shared.TEMPLATE3)), arguments.number))))
