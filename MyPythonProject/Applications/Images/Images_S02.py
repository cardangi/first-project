# -*- coding: ISO-8859-1 -*-
__author__ = 'Xavier ROSSET'


# ========
# Imports.
# ========
import re
import sys
import os.path
import argparse
from .. import shared


# ==========
# Functions.
# ==========
def deco1(f):
    def noname(x, y):
        return "{}{}".format(x, f(y))
    return noname


def deco2(f):
    def noname(x, y):
        return "{}\n{}".format(x, f(y))
    return noname


def func1(x):
    return "\t{}".format(x).expandtabs(5)


def func2(x):
    return x


def validdirectory(d):
    if not os.path.isdir(d):
        raise argparse.ArgumentTypeError('"{}" is not a valid directory'.format(d))
    if not os.access(d, os.R_OK):
        raise argparse.ArgumentTypeError('"{}" is not a readable directory'.format(d))
    return d


# =================
# Arguments parser.
# =================
parser = argparse.ArgumentParser()
parser.add_argument("directory", type=validdirectory)
arguments = parser.parse_args()


# ================
# Initializations.
# ================
o, first, regex = "", True, re.compile(r"^.+\.jpg$", re.IGNORECASE)


# ==============================
# Mise en place des décorateurs.
# ==============================
field = deco1(func1)


# ===============
# Main algorithm.
# ===============
if not os.path.isdir(arguments.directory):
    sys.exit()
for file in shared.directorytree(arguments.directory):
    if regex.match(file):
        img = shared.Images(file)
        line = deco1(func2)
        if not first:
            line = deco2(func2)
        o = line(o, file.ljust(35))
        if "originaldatetime" in img:
            o = field(o, img["originaldatetime"].ljust(30))
        if "make" in img:
            o = field(o, img["make"].ljust(20))
        if "model" in img:
            o = field(o, img["model"].ljust(35))
        # if "copyright" in img:
        #     o = field(o, img["copyright"].ljust(35))
        if first:
            first = False
if o:
    print(o)
