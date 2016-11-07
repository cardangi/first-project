# -*- coding: ISO-8859-1 -*-
import argparse
import logging
import shutil
import json
import os

__author__ = 'Xavier ROSSET'


# ==========
# Functions.
# ==========


# =================
# Arguments parser.
# =================
parser = argparse.ArgumentParser()
parser.add_argument("file", type=argparse.FileType(mode="r"))


# =========
# Contants.
# =========
JSON, TABSIZE = os.path.join(os.path.expandvars("%TEMP%"), "arguments.json"), 3


# ================
# Initializations.
# ================
arguments = parser.parse_args()


# ========
# Logging.
# ========
logger = logging.getLogger("%s.%s" % (__package__, os.path.basename(__file__)))


# ===============
# Main algorithm.
# ===============
for src, dst in json.load(arguments.file):
    if not os.path.exists(os.path.dirname(dst)):
        os.makedirs(os.path.dirname(dst))
    shutil.copy2(src=src, dst=dst)
