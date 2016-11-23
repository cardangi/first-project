# -*- coding: utf-8 -*-
import os
import json
import argparse
import datetime
from Applications.Database.DigitalAudioFiles.shared import select
from Applications.shared import WRITE, LOCAL, TEMPLATE2, UTF8, dateformat

__author__ = 'Xavier ROSSET'


# ==========
# Functions.
# ==========
def validdb(arg):
    if not os.path.exists(arg):
        raise argparse.ArgumentTypeError('"{0}" doesn\'t exist.'.format(arg))
    return arg


def thatfunc(d):
    if isinstance(d, datetime.datetime):
        return dateformat(LOCAL.localize(d), TEMPLATE2)
    return d


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
with open(os.path.join(os.path.expandvars("%TEMP%"), "digitalaudiofiles.json"), mode=WRITE, encoding=UTF8) as fw:
    json.dump([list(map(thatfunc, item)) for item in select(arguments.database)], fw, indent=4, ensure_ascii=False)
