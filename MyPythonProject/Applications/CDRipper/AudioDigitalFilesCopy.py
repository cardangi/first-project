# -*- coding: ISO-8859-1 -*-
from mutagen import File, MutagenError
from contextlib import ExitStack
import argparse
import logging
import shutil
import sys
import os
import re
from .. import shared


__author__ = 'Xavier ROSSET'


# ============
# Local names.
# ============
dirname, basename, exists = os.path.dirname, os.path.basename, os.path.exists


# ==========
# Functions.
# ==========
def log(arg1, arg2):
    logger.debug("Copy file.")
    logger.debug("\tSource\t\t: {0}".format(arg1).expandtabs(3))
    logger.debug("\tDestination : {0}".format(arg2).expandtabs(3))


def validdirectory(d):
    if not exists(d):
        raise argparse.ArgumentTypeError('"{0}" isn\'t a valid output directory.'.format(d))
    return d


# =================
# Arguments parser.
# =================
parser = argparse.ArgumentParser()
parser.add_argument("odirectory", type=validdirectory)
parser.add_argument("-t", "--test", action="store_true")


# ==========
# Constants.
# ==========
IDIRECTORY = r"F:\\`X5"


# ================
# Initializations.
# ================
arguments = parser.parse_args()


# ===================
# Regular expression.
# ===================
regex = re.compile(r"^{0}".format(IDIRECTORY), re.IGNORECASE)


# ========
# Logging.
# ========
logger = logging.getLogger("%s.%s" % (__package__, basename(__file__)))


# ===============
# Main algorithm.
# ===============

# 1. Is IDIRECTORY a valid input directory?
if not exists(IDIRECTORY):
    logger.debug('"{0}" doesn\'t exist. Can\'t run script.'.format(IDIRECTORY))
    sys.exit(100)

# 2. Copy found FLAC files from input directory to output directory.
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
