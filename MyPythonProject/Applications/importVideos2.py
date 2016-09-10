# -*- coding: ISO-8859-1 -*-
__author__ = 'Xavier ROSSET'


# =================
# Absolute imports.
# =================
from datetime import datetime
from pytz import timezone
import argparse
import logging
import shutil
import os


# =================
# Relative imports.
# =================
from . import shared


# ==========
# Functions.
# ==========
def validpath(p):
    if not os.path.exists(p):
        raise argparse.ArgumentTypeError('"{0}" doesn\'t exist'.format(p))
    if not os.path.isdir(p):
        raise argparse.ArgumentTypeError('"{0}" is not a directory'.format(p))
    return p


# =================
# Arguments parser.
# =================
parser = argparse.ArgumentParser()
parser.add_argument("src", type=validpath)
parser.add_argument("--dst", nargs="?", default=r"G:\Videos\AVCHD Videos", type=validpath)
parser.add_argument("--extensions", nargs="*", default="mts")
parser.add_argument("--test", action="store_true")


# ========
# Logging.
# ========
logger = logging.getLogger("%s.%s" % ("Applications", os.path.basename(__file__)))


# ================
# Initializations.
# ================
arguments = parser.parse_args()


# ===============
# Main algorithm.
# ===============


#     ---------------------------------------------------
#  1. Liste distincte des dates de dernière modification.
#     ---------------------------------------------------
folders = sorted([folder for folder in {shared.dateformat(timezone("UTC").localize(datetime.utcfromtimestamp(os.path.getmtime(file))).astimezone(timezone(shared.DFTTIMEZONE)), shared.TEMPLATE5)
                                        for file in shared.filesinfolder(*arguments.extensions, folder=arguments.src)}])


#     -------------------------
#  2. Création des répertoires.
#     -------------------------
for folder in folders:
    if not os.path.exists(os.path.join(arguments.dst, folder)):
        logger.debug('Create folder "{0}".'.format(os.path.join(arguments.dst, folder)))
        if not arguments.test:
            os.mkdir(os.path.join(arguments.dst, folder))


#     -------------------
#  3. Copie des fichiers.
#     -------------------
for file in shared.filesinfolder(*arguments.extensions, folder=arguments.src):
    dst = os.path.join(arguments.dst, shared.dateformat(timezone("UTC").localize(datetime.utcfromtimestamp(os.path.getmtime(file))).astimezone(timezone(shared.DFTTIMEZONE)), shared.TEMPLATE5))
    logger.debug("Copy file.")
    logger.debug('\tSource     : "{0}".'.format(file).expandtabs(3))
    logger.debug('\tDestination: "{0}".'.format(dst).expandtabs(3))
    if not arguments.test:
        try:
            shutil.copy2(src=file, dst=dst)
        except OSError:
            logger.debug("\tCopy failed.".expandtabs(4))
        else:
            logger.debug("\tCopy succeeded.".expandtabs(4))
