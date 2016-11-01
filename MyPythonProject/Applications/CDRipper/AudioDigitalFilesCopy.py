# -*- coding: ISO-8859-1 -*-
from mutagen import File, MutagenError
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
parser.add_argument("-t", "--test", action="store_true")


# ============
# Local names.
# ============
dirname, basename = os.path.dirname, os.path.basename

# ==========
# Constants.
# ==========
IDIRECTORY = r"F:\\`X5"


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
logger = logging.getLogger("%s.%s" % (__package__, basename(__file__)))


# ==========
# Functions.
# ==========
def log(arg1, arg2):
    logger.debug("Copy file.")
    logger.debug("\tSource\t\t: {0}".format(arg1).expandtabs(3))
    logger.debug("\tDestination : {0}".format(arg2).expandtabs(3))


# ===============
# Main algorithm.
# ===============
if os.path.exists(IDIRECTORY):
    top = True
if top:
    stack = ExitStack()
    stack.callback(shutil.rmtree, IDIRECTORY)
    with stack:
        for fil in shared.filesinfolder(folder=IDIRECTORY):
            try:
                audio = File(fil)
            except MutagenError:
                continue
            if "audio/flac" in audio.mime:
                fil = os.path.normpath(fil)
                dst = dirname(regex.sub(arguments.odirectory, fil))
                if arguments.test:
                    log(fil, dst)
                    continue
                while True:
                    try:
                        shutil.copy2(src=fil, dst=dst)
                    except FileNotFoundError:
                        os.makedirs(dst)
                    else:
                        log(fil, dst)
                        break
