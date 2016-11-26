# -*- coding: ISO-8859-1 -*-
import os
import yaml
import logging
import argparse
from contextlib import ExitStack
from logging.config import dictConfig
from Applications.AudioCD.shared import RippedCD, digitalaudiobase, rippinglog


__author__ = 'Xavier ROSSET'


# =================
# Arguments parser.
# =================
parser = argparse.ArgumentParser()
parser.add_argument("file", help="tags file")
parser.add_argument("profile", help="rip profile")
parser.add_argument("-t", "--test", action="store_true")


# ========
# Logging.
# ========
with open(os.path.join(os.path.expandvars("%_COMPUTING%"), "logging.yml"), encoding="UTF_8") as fp:
    dictConfig(yaml.load(fp))
logger = logging.getLogger("Ripper.{0}".format(os.path.splitext(os.path.basename(__file__))[0]))


# ============
# Local names.
# ============
exists, join, expandvars = os.path.exists, os.path.join, os.path.expandvars


# ==========
# Variables.
# ==========
obj, arguments = [], parser.parse_args()


# ===============
# Main algorithm.
# ===============
stack = ExitStack()
try:
    rippedcd = stack.enter_context(RippedCD(arguments.profile, arguments.file, arguments.test))
except ValueError as e:
    logger.debug(e)
else:
    with stack:
        if arguments.profile in ["default", "selftitled"]:

            #  --> 1. Digital audio files database.
            digitalaudiobase(rippedcd.new)

            #  --> 2. Ripped CD database.
            rippinglog(rippedcd.new)
