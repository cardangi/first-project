# -*- coding: ISO-8859-1 -*-
__author__ = 'Xavier ROSSET'


# ========
# Imports.
# ========
from os.path import exists, join, normpath
from sortedcontainers import SortedDict
from pprint import PrettyPrinter
from Applications import shared
import argparse
import glob


# ==========
# Functions.
# ==========
def validyear(s):
    import re
    regex = re.compile(r"^(19[6-9]|20[0-2])[0-9]$")
    if not regex.match(s):
        raise argparse.ArgumentTypeError('"{}" is not a valid year'.format(s))
    return int(s)


# =================
# Arguments parser.
# =================
parser = argparse.ArgumentParser()
parser.add_argument("year", type=validyear)
arguments = parser.parse_args()


# ================
# Initializations.
# ================
d1, d2 = SortedDict(), SortedDict()


# ===============
# Main algorithm.
# ===============
for m in range(1, 13):
    curdir = normpath(join("h:/", "{}{}".format(arguments.year, str(m).zfill(2))))
    if exists(curdir):
        d1.clear()
        with shared.chgcurdir(curdir):
            for file in glob.iglob("*.jpg"):
                img = shared.Images(join(curdir, file))
                if "originaldatetime" in img:
                    ccyymm = "{}{}".format(img["originalyear"], str(img["originalmonth"]).zfill(2))
                    if ccyymm in d1:
                        d1[ccyymm] += 1
                    else:
                        d1[ccyymm] = 1
            d2[curdir] = SortedDict(zip(list(d1.keys()), [d1[key] for key in list(d1.keys())]))
if d2:
    PrettyPrinter().pprint(d2)
