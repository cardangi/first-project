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
parser.add_argument("input", action=GetUID)
parser.add_argument("-d", "--db", dest="database", default=os.path.join(os.path.expandvars("%_COMPUTING%"), "database.db"), type=validdb)


# ================
# Initializations.
# ================
arguments = parser.parse_args()


# ===============
# Main algorithm.
# ===============
sys.exit(deletefromuid(*arguments.uid, db=arguments.database))
