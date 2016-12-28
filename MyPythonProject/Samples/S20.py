# -*- coding: utf-8 -*-
import os
import sys
import yaml
import logging
from logging.config import dictConfig
from subprocess import run
from Applications.parsers import readtable
from Applications.Database.Tables.shared import isdeltareached, update

__author__ = 'Xavier ROSSET'


# ========
# Logging.
# ========
with open(os.path.join(os.path.expandvars("%_COMPUTING%"), "logging.yml"), encoding="UTF_8") as fp:
    dictConfig(yaml.load(fp))
logger = logging.getLogger("Tables.{0}".format(os.path.splitext(os.path.basename(__file__))[0]))


# ==========
# Constants.
# ==========
MAPPING = {False: 1, True: 0}


# ==========
# Arguments.
# ==========
readtable.add_argument("-d", "--delta", help="delta required to trigger action(s)", nargs="?", default="10", const="10", type=int)
arguments = readtable.parse_args()


# ===============
# Main algorithm.
# ===============
status = 0
if isdeltareached(arguments.uid, arguments.table, arguments.database, arguments.delta):
    process = run(["C:\Program Files\Sandboxie\Start.exe", "/box:GNUCash", "delete_sandbox_silent"])
    logger.debug(process.returncode)
    if not process.returncode:
        status = update(arguments.uid, db=arguments.database, table=arguments.table)
logger.debug(status)
sys.exit(status)
