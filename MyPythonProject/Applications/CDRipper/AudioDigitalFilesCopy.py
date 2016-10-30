# -*- coding: ISO-8859-1 -*-
from contextlib import ExitStack
from Applications import shared
import argparse
import logging
import shutil
import os
import re

__author__ = 'Xavier ROSSET'


# =================
# Arguments parser.
# =================
parser = argparse.ArgumentParser()
parser.add_argument("odirectory")


# ==========
# Constants.
# ==========
IDIRECTORY = r"F:\\`ToBeCopied"


# ================
# Initializations.
# ================
top, arguments = False, parser.parse_args()


# ===================
# Regular expression.
# ===================
regex = re.compile(r"^{0}".format(IDIRECTORY), re.IGNORECASE)


# ========
# Logging.
# ========
logger = logging.getLogger("%s.%s" % (__package__, os.path.basename(__file__)))


# ===============
# Main algorithm.
# ===============
if os.path.exists(IDIRECTORY):
    top = True
if top:
    stack = ExitStack()
    stack.callback(shutil.rmtree, IDIRECTORY)
    with stack:
        for fil in shared.filesinfolder("flac", folder=IDIRECTORY):
            dst = os.path.dirname(os.path.dirname(regex.sub(arguments.odirectory, os.path.normpath(fil))))
            while True:
                try:
                    shutil.copy2(src=fil, dst=dst)
                except FileNotFoundError:
                    os.makedirs(dst)
                else:
                    logger.debug("Copy file.")
                    logger.debug("\tSource\t\t: {0}".format(os.path.normpath(fil)).expandtabs(3))
                    logger.debug("\tDestination : {0}".format(dst).expandtabs(3))
                    break
