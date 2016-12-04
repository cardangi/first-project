# -*- coding: utf-8 -*-
import os
import re
import sys
import argparse
from Applications.shared import validdb
from Applications.Database.AudioCD.shared import deletefromuid

__author__ = 'Xavier ROSSET'


# ================
# Initializations.
# ================
digits = r"\d(?:\d(?:\d(?:\d)?)?)?"


# ====================
# Regular expressions.
# ====================
rex1, rex2 = re.compile(digits), re.compile(r"^({0})\b\s?-\s?\b({0})$".format(digits))


# =================
# Arguments parser.
# =================
parser = argparse.ArgumentParser()
parser.add_argument("-d", "--db", dest="database", default=os.path.join(os.path.expandvars("%_COMPUTING%"), "database.db"), type=validdb)


# ================
# Initializations.
# ================
arguments = parser.parse_args()


# ===============
# Main algorithm.
# ===============
while True:
    arg = input("Please enter record(s) unique ID: ")

    # Ranged Unique ID.
    match = rex2.match(arg)
    if match:
        uid = range(int(match.group(1)), int(match.group(2)) + 1)
        break

    # Singled Unique ID.
    uid = rex1.findall(arg)
    if uid:
        uid = map(int, uid)
        break

sys.exit(deletefromuid(*list(uid), db=arguments.database))
