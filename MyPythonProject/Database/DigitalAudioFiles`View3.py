# -*- coding: utf-8 -*-
import os
import json
import yaml
import logging
import argparse
import datetime
from logging.config import dictConfig
from Applications.Database.DigitalAudioFiles.shared import select
from Applications.shared import WRITE, LOCAL, TEMPLATE2, UTC, UTF8, dateformat

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


def thatotherfunc(b):
    if b:
        return "Default"
    return "Info"


# =================
# Arguments parser.
# =================
parser = argparse.ArgumentParser()
parser.add_argument("-d", "--db", dest="database", default=os.path.join(os.path.expandvars("%_COMPUTING%"), "database.db"), type=validdb)
parser.add_argument("-o", "--output", default=os.path.join(os.path.expandvars("%TEMP%"), "digitalaudiofiles.json"), type=argparse.FileType(mode=WRITE, encoding=UTF8))
parser.add_argument("-l", "--logging", default=os.path.join(os.path.expandvars("%_COMPUTING%"), "logging.yml"), type=argparse.FileType(encoding=UTF8))
parser.add_argument("-u", "--debug", action="store_true")


# ================
# Initializations.
# ================
arguments = parser.parse_args()


# ========
# Logging.
# ========
dictConfig(yaml.load(arguments.logging))
logger = logging.getLogger("{1}.{0}".format(os.path.splitext(os.path.basename(__file__))[0], thatotherfunc(arguments.debug)))
logger.debug(__file__)


# ===============
# Main algorithm.
# ===============
json.dump([dateformat(UTC.localize(datetime.datetime.utcnow()).astimezone(LOCAL), TEMPLATE2), [list(map(thatfunc, item)) for item in select(arguments.database)]], arguments.output, indent=4, ensure_ascii=False)
