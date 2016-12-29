# -*- coding: utf-8 -*-
import os
import sys
import yaml
import logging
import argparse
from subprocess import run
from logging.config import dictConfig
from Applications.shared import validdb, DATABASE
from Applications.Database.Tables.shared import isdeltareached, update

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
UID = 123456798
TABLE = "rundates"


# ================
# Initializations.
# ================
status, arguments = 0, parser.parse_args()


# ===============
# Main algorithm.
# ===============
if isdeltareached(UID, TABLE, arguments.database):
    process = run(["C:\Program Files\Sandboxie\Start.exe", "/box:GNUCash", "delete_sandbox_silent"])
    logger.debug(process.returncode)
    if not process.returncode:
        status = update(UID, TABLE, arguments.database)
logger.debug(status)
sys.exit(status)
