# -*- coding: ISO-8859-1 -*-
import logging
import json
import sys
import os
import re

__author__ = 'Xavier ROSSET'


# ==========
# Constants.
# ==========
JSON = os.path.join(os.path.expandvars("%TEMP%"), "arguments.json")


# ====================
# Regular expressions.
# ====================
regex = re.compile("\d(?:\d(?:\d(?:\d)?)?)?")


# ================
# Initializations.
# ================
arguments, status = None, 100


# ========
# Logging.
# ========
logger = logging.getLogger("%s.%s" % (__package__, os.path.basename(__file__)))


# ===============
# Main algorithm.
# ===============
while True:
    numbers = input("Please enter record(s) unique ID: ")
    arguments = regex.findall(numbers)
    if arguments:
        break
if arguments:
    # logger.debug(arguments)
    status = 0
    with open(JSON, mode="w") as fp:
        json.dump(arguments, fp)
sys.exit(status)
