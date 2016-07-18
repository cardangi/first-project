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
import sqlite3
import csv
import os
import re


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
HEADERS = ["tag", "value"]
PROFILES = ["fdk v0.1.3"]
EXCLUDED = ["mediaprovider", "purchasedate", "source"]
OUTPUT = Template("$key=$value")
REGEX = r"^((?:1|2)\.(?:{0})(?:{1})(?:{2})\.\d\.)\d{{2}}$"


# ==========
# Variables.
# ==========
d, rex = {}, re.compile(REGEX.format(shared.DFTYEARREGEX, shared.DFTMONTHREGEX, shared.DFTDAYREGEX), re.IGNORECASE)


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


def existingprofile(p):
    if p.lower() not in PROFILES:
        raise argparse.ArgumentTypeError('"{}" is not a valid profile'.format(p))
    return p


def rtvcodec(c):
    code = None
    conn = sqlite3.connect(shared.DATABASE, detect_types=sqlite3.PARSE_DECLTYPES)
    conn.row_factory = sqlite3.Row
    for data in conn.cursor().execute("SELECT definitions FROM encoders WHERE encoder=?", (c,)):
        code = data["definitions"].decode(shared.DFTENCODING).split(";")[0]
    conn.close()
    return code


# =================
# Arguments parser.
# =================
parser = argparse.ArgumentParser()
parser.add_argument("input", help="tags file", type=existingfile)
parser.add_argument("profile", help="tags profile", type=existingprofile)
arguments = parser.parse_args()


# ===============
# Main algorithm.
# ===============


#     ----------
#  1. Read tags.
#     ----------
with open(arguments.input, encoding=shared.UTF16) as fr:
    reader = csv.DictReader(fr, delimiter="=", fieldnames=HEADERS)
    for row in reader:
        d[row["tag"].strip().strip(shared.UTF16BOM).lower()] = row["value"].strip()

#     ------
#  2. Codec.
#     ------
codec = rtvcodec(arguments.profile)

#     -------------
#  3. Tagging time.
#     -------------
d["taggingtime"] = shared.dateformat(datetime.now(tz=timezone(shared.DFTTIMEZONE)), shared.TEMPLATE3)

#     -----------
#  4. Encoded by.
#     -----------
d["encodedby"] = "dBpoweramp Batch Converter on %s" % (shared.dateformat(datetime.now(tz=timezone(shared.DFTTIMEZONE)), shared.TEMPLATE3),)

#     --------------
#  5. Encoding time.
#     --------------
d["encodingtime"] = int(datetime.now(tz=timezone(shared.DFTTIMEZONE)).timestamp())

#     ----------
#  6. Albumsort.
#     ----------
if codec:
    d["albumsort"] = rex.sub(r"\g<1>%s" % (codec,), d["albumsort"])

#     -----------
#  7. Write tags.
#     -----------
with open(arguments.input, mode="w", encoding=shared.UTF16) as fw:
    for k, v in d.items():
        if k not in EXCLUDED:
            fw.write("%s\n" % (OUTPUT.substitute(key=k, value=v),))
