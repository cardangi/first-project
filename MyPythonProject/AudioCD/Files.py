# -*- coding: ISO-8859-1 -*-
import argparse
import logging
import json
import os

__author__ = 'Xavier ROSSET'


# =================
# Arguments parser.
# =================
parser = argparse.ArgumentParser()
parser.add_argument("ifile")


# ==========
# Constants.
# ==========
JSON = os.path.join(os.path.expandvars("%TEMP%"), "files.json")


# ================
# Initializations.
# ================
obj, arguments = list(), parser.parse_args()


# ========
# Logging.
# ========
logger = logging.getLogger("%s.%s" % (__package__, os.path.basename(__file__)))


# ===============
# Main algorithm.
# ===============
if os.path.exists(JSON):
    with open(JSON) as fp:
        obj = json.load(fp)
obj.append(arguments.ifile)
with open(JSON, mode="w") as fp:
    json.dump(list(set(obj)), fp, indent=4, sort_keys=True)


