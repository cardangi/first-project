# -*- coding: utf-8 -*-
import os
import sys
import yaml
import logging
import argparse
import itertools
from subprocess import run
from logging.config import dictConfig
from Applications.shared import validdb, DATABASE
from Applications.Database.Tables.shared import isdeltareached, update

__author__ = 'Xavier ROSSET'


# ==========
# Arguments.
# ==========
parser = argparse.ArgumentParser()
parser.add_argument("database", nargs="?", default=DATABASE, type=validdb, help="Read/Updated database")


# ===============
# Main algorithm.
# ===============
if __name__ == "__main__":

    #  1. --> Logging.
    with open(os.path.join(os.path.expandvars("%_COMPUTING%"), "logging.yml"), encoding="UTF_8") as fp:
        dictConfig(yaml.load(fp))
    logger = logging.getLogger("Applications.Database.Tables")

    #  2. --> Initializations.
    UID = 123456798

    #  3. --> Initializations.
    status, arguments = 0, parser.parse_args()
    isdeltareached = functools.partial(isdeltareached, UID, "rundates")
    update = functools.partial(update, UID, "rundates")

    #  4. --> Main algorithm.
    if isdeltareached(arguments.database):
        process = run(["C:\Program Files\Sandboxie\Start.exe", "/box:GNUCash", "delete_sandbox_silent"])
        logger.debug(process.returncode)
        if not process.returncode:
            status = update(arguments.database)

    #  5. --> Exit algorithm.
    logger.debug(status)
    sys.exit(status)
