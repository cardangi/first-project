# -*- coding: ISO-8859-1 -*-
from Applications.AudioCD.shared import validdelay, FLACFilesCollection
from logging.config import dictConfig
import argparse
import logging
import sched
import yaml
import sys
import os

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


def updatetags(d, test=True):
    FLACFilesCollection(d)(test=test)


# =================
# Arguments parser.
# =================
parser = argparse.ArgumentParser()
parser.add_argument("drive", type=validdrive)
parser.add_argument("-d", "--delay", type=validdelay, default="0")
parser.add_argument("-t", "--test", action="store_true")


# =========
# Contants.
# =========
TABSIZE = 3


# ================
# Initializations.
# ================
arguments = parser.parse_args()


# ========
# Logging.
# ========
with open(os.path.join(os.path.expandvars("%_COMPUTING%"), "logging.yml"), encoding="UTF_8") as fp:
    dictConfig(yaml.load(fp))
logger = logging.getLogger("Ripper.{0}".format(os.path.splitext(os.path.basename(__file__))[0]))
logger.debug("Delay: {0} second(s).".format(arguments.delay))
logger.debug("Test : {0}.".format(arguments.test))


# ===============
# Main algorithm.
# ===============

# Mise à jour immédiate.
if not arguments.delay:
    updatetags(arguments.drive, test=arguments.test)
    sys.exit(0)

# Mise à jour différée.
s = sched.scheduler()
s.enter(arguments.delay, 1, updatetags, argument=(arguments.drive,), kwargs={"test": arguments.test})
s.run()
