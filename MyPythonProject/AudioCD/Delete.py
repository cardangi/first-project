# -*- coding: ISO-8859-1 -*-
import os
import re
import argparse
from Applications.Database.RippedCD.shared import deletefromuid

__author__ = 'Xavier ROSSET'


# ==========
# Functions.
# ==========
def validdb(arg):
    if not os.path.exists(arg):
        raise argparse.ArgumentTypeError('"{0}" doesn\'t exist.'.format(arg))
    return arg


# ====================
# Regular expressions.
# ====================
regex = re.compile("\d(?:\d(?:\d(?:\d)?)?)?")


# =================
# Arguments parser.
# =================
parser = argparse.ArgumentParser()
parser.add_argument("-d", "--db", dest="database", default=os.path.join(os.path.expandvars("%_COMPUTING%"), "database.db"), type=validdb)


# ===============
# Main algorithm.
# ===============
arguments = parser.parse_args()


# ===============
# Main algorithm.
# ===============
while True:
    numbers = input("Please enter record(s) unique ID: ")
    args = regex.findall(numbers)
    if args:
        break
deletefromuid(*args)
