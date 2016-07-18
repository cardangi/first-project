# -*- coding: ISO-8859-1 -*-
__author__ = 'Xavier ROSSET'


# =================
# Absolute imports.
# =================
from datetime import datetime
from string import Template
from pytz import timezone
import argparse
import logging
import csv
import os


# =================
# Relative imports.
# =================
from Applications import shared


# ========
# Logging.
# ========
logger = logging.getLogger("%s.%s" % (__package__, os.path.basename(__file__)))


# ==========
# Constants.
# ==========
EXCLUDED = []
HEADERS = ["tag", "value"]
OUTPUT = Template("$key=$value")


# ==========
# Variables.
# ==========
tags = {}


# ==========
# Functions.
# ==========
def existingfile(f):
    if not os.path.exists(f):
        raise argparse.ArgumentTypeError('"{0}" is not a valid file'.format(f))
    if not os.path.isfile(f):
        raise argparse.ArgumentTypeError('"{0}" is not a valid file'.format(f))
    if not os.access(f, os.R_OK):
        raise argparse.ArgumentTypeError('"{}" is not a readable file'.format(f))
    return f


# =================
# Arguments parser.
# =================
parser = argparse.ArgumentParser()
parser.add_argument("input", help="tags file", type=existingfile)
arguments = parser.parse_args()


# ==============
# Start logging.
# ==============
logger.info("{0:=^138}".format(" {0} ".format(shared.dateformat(datetime.now(tz=timezone(shared.DFTTIMEZONE)), shared.TEMPLATE1))))
logger.info('START "%s".' % (os.path.basename(__file__),))


# ===============
# Main algorithm.
# ===============

#     ----------
#  1. Read tags.
#     ----------
with open(arguments.input, encoding=shared.UTF16) as fr:
    reader = csv.DictReader(fr, delimiter="=", fieldnames=HEADERS)
    for row in reader:
        tags[row["tag"].strip("{0} ".format(shared.UTF16BOM)).lower()] = row["value"].strip()

#     --------
#  2. Logging.
#     --------
width = max(len(key) for key in sorted(tags.keys()))
for key in sorted(tags.keys()):
    logger.debug("{0:.<{1}}: {2}".format(key, width+1, tags[key]))

#     --------------
#  3. Tagging time.
#     --------------
tags["taggingtime"] = shared.dateformat(datetime.now(tz=timezone(shared.DFTTIMEZONE)), shared.TEMPLATE3)

#     -----------
#  4. Write tags.
#     -----------
with open(arguments.input, mode="w", encoding=shared.UTF16) as fw:
    for k, v in tags.items():
        if k not in EXCLUDED:
            fw.write("%s\n" % (OUTPUT.substitute(key=k, value=v),))


# ============
# End logging.
# ============
logger.info('END "%s".' % (os.path.basename(__file__),))
