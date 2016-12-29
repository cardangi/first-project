# -*- coding: utf-8 -*-
from Applications.Database.Tables.shared import isdeltareached, update
from Applications.shared import DATABASE, WRITE, validdb
from logging.config import dictConfig
import argparse
import logging
import zipfile
import yaml
import sys
import os

__author__ = 'Xavier ROSSET'


# ========
# Logging.
# ========
with open(os.path.join(os.path.expandvars("%_COMPUTING%"), "logging.yml"), encoding="UTF_8") as fp:
    dictConfig(yaml.load(fp))
logger = logging.getLogger("Tables.{0}".format(os.path.splitext(os.path.basename(__file__))[0]))


# ==========
# Arguments.
# ==========
parser = argparse.ArgumentParser()
parser.add_argument("database", nargs="?", default=DATABASE, type=validdb, help="Read/Updated database")


# ==========
# CONSTANTS.
# ==========
UID = 123456799
TABLE = "rundates"
FILES = [r"C:\Users\Xavier\Documents\Database.kdbx", r"Y:\Database.key"]


# ================
# Initializations.
# ================
status, arguments = 0, parser.parse_args()


# ===============
# Main algorithm.
# ===============
if isdeltareached(UID, TABLE, arguments.database):
    with zipfile.ZipFile(os.path.join("F:\\", "passwords.7z"), WRITE) as myzip:
        if all(map(os.path.exists, FILES)):
            for file in FILES:
                myzip.write(file, arcname=os.path.basename(file))
            status = update(UID, TABLE, arguments.database)
logger.debug(status)
sys.exit(status)
