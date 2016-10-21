# -*- coding: ISO-8859-1 -*-
import argparse
import logging
import json
import os
import re

__author__ = 'Xavier ROSSET'


# =================
# Arguments parser.
# =================
parser = argparse.ArgumentParser()
parser.add_argument("ifile")
parser.add_argument("ofile")


# ==========
# Constants.
# ==========
JSON = os.path.join(os.path.expandvars("%TEMP%"), "dirname.json")


# ================
# Initializations.
# ================
obj, arguments = list(), parser.parse_args()


# ===================
# Regular expression.
# ===================
regex = re.compile("\u00BF")


# ========
# Logging.
# ========
logger = logging.getLogger("%s.%s" % (__package__, os.path.basename(__file__)))
logger.debug("Input file\t: ".format(arguments.ifile).expandtabs(3))
logger.debug("Output file: ".format(arguments.ofile))


# ===================================
# Store dirname if invalid character.
# ===================================
# --> Upside down question mark: "¿".
if regex.search(os.path.dirname(arguments.ofile)):
    if os.path.exists(JSON):
        with open(JSON) as fp:
            obj = json.load(fp)
    obj.append(os.path.dirname(arguments.ofile))
    with open(JSON, mode="w") as fp:
        json.dump(list(set(obj)), fp, indent=4, sort_keys=True)


