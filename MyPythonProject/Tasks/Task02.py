# -*- coding: utf-8 -*-
from Applications.Database.Tables.shared import isdeltareached, update
from Applications.shared import DATABASE, WRITE, validdb, zipfiles
from logging.config import dictConfig
import functools
import argparse
import logging
import zipfile
import yaml
import sys
import os

__author__ = 'Xavier ROSSET'


# ================
# Initializations.
# ================
zipfiles = functools.partial(zipfiles, r"F:\passwords.7z", r"C:\Users\Xavier\Documents\Database.kdbx", r"Y:\Database.key")


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
    logger = logging.getLogger("zipfiles.{0}".format(os.path.splitext(os.path.basename(__file__))[0]))

    #  2. --> Initializations.
    UID = 123456799

    #  3. --> Initializations.
    status, arguments = 0, parser.parse_args()

    #  4. --> Main.
    if isdeltareached(UID, arguments.database):
        try:
            zipfiles()
        except OSError as err:
            logger.exception(err)
        else:
            status = updaterundates(UID, arguments.database)

logger.info(status)
sys.exit(status)


# FILES = [r"C:\Users\Xavier\Documents\Database.kdbx", r"Y:\Database.key"]
