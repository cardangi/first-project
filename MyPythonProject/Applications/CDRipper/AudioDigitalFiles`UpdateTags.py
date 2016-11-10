# -*- coding: ISO-8859-1 -*-
import argparse
import logging
import sched
import sys
import os
from .Modules import shared

__author__ = 'Xavier ROSSET'


# ============
# Local names.
# ============
basename, dirname, exists = os.path.basename, os.path.dirname, os.path.exists


# ==========
# Functions.
# ==========
def validdrive(d):
    if not os.path.exists(d):
        raise argparse.ArgumentTypeError('"{0}" isn\'t a valid drive.'.format(d))
    return d


# =================
# Arguments parser.
# =================
parser = argparse.ArgumentParser()
parser.add_argument("drive", type=validdrive)
parser.add_argument("-d", "--delay", type=shared.validdelay, default="0")
parser.add_argument("-t", "--test", action="store_true")


# =========
# Contants.
# =========
TABSIZE = 3


# ================
# Initializations.
# ================
arguments = parser.parse_args()
collection = shared.FLACFilesCollection(arguments.drive)


# ========
# Logging.
# ========
logger = logging.getLogger("%s.%s" % (__package__, basename(__file__)))


# ===============
# Main algorithm.
# ===============
logger.debug("{0:>5d} FLAC file(s) found.".format(len(collection)))

# Mise à jour immédiate.
if not arguments.delay:
    collection(test=arguments.test)
    sys.exit(0)

# Mise à jour différée.
s = sched.scheduler()
s.enter(arguments.delay, 1, collection, kwargs={"test": arguments.test})
s.run()
