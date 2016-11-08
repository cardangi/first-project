# -*- coding: ISO-8859-1 -*-
"""
Exécuter des copies de fichiers en utilisant les arguments énumérés dans le fichier JSON reçu en paramètre.
"""
from collections import MutableSequence
import argparse
import logging
import shutil
import sched
import json
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
def validdelay(d):
    try:
        delay = int(d)
    except ValueError:
        raise argparse.ArgumentTypeError('"{0}" isn\'t a valid delay.'.format(d))
    if delay > 60:
        return 60
    return delay


# =================
# Arguments parser.
# =================
parser = argparse.ArgumentParser()
parser.add_argument("file", type=argparse.FileType(mode="r"))
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
logger = logging.getLogger("%s.%s" % (__package__, basename(__file__)))


# ========
# Classes.
# ========
class CopyFilesFrom(MutableSequence):

    def __init__(self, filobj):
        self._seq = json.load(filobj)

    def __getitem__(self, item):
        return self._seq[item]

    def __setitem__(self, key, value):
        self._seq[key] = value

    def __delitem__(self, key):
        del self._seq[key]

    def __len__(self):
        return len(self._seq)

    def __call__(self, *args, **kwargs):
        for src, dst in self:
            if not exists(src):
                logger.debug('"{0}" doesn\'t exist.'.format(src))
                continue
            logger.debug("Copy.")
            if not exists(dirname(dst)):
                logger.debug('\t"{0}" created.'.format(dirname(dst)).expandtabs(TABSIZE))
                if not kwargs["test"]:
                    os.makedirs(dirname(dst))
            logger.debug('\tSource     : "{0}"'.format(src).expandtabs(TABSIZE))
            logger.debug('\tDestination: "{0}"'.format(dst).expandtabs(TABSIZE))
            if not kwargs["test"]:
                shutil.copy2(src=src, dst=dst)

    def insert(self, index, value):
        self._seq.insert(index, value)


# ===============
# Main algorithm.
# ===============
if not arguments.delay:
    CopyFilesFrom(arguments.file)(test=arguments.test)
    sys.exit(0)
s = sched.scheduler()
s.enter(arguments.delay, 1, CopyFilesFrom(arguments.file), kwargs={"test": arguments.test})
s.run()
