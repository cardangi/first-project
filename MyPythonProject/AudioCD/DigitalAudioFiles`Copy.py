# -*- coding: ISO-8859-1 -*-
"""
Ex�cuter des copies de fichiers en utilisant les arguments �num�r�s dans le fichier JSON re�u en param�tre.
"""
from Applications.AudioCD.shared import validdelay
from collections import MutableSequence
from logging.config import dictConfig
import argparse
import logging
import shutil
import sched
import yaml
import json
import sys
import os

__author__ = 'Xavier ROSSET'


# ============
# Local names.
# ============
basename, dirname, exists = os.path.basename, os.path.dirname, os.path.exists


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


# ========
# Classes.
# ========
class CopyFilesFrom(MutableSequence):

    logger = logging.getLogger("{0}.CopyFilesFrom".format(os.path.splitext(os.path.basename(__file__))[0]))

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
        self.logger.debug("Test       : {0}".format(kwargs["test"]))
        for src, dst in self:
            if not exists(src):
                self.logger.debug('"{0}" doesn\'t exist.'.format(src))
                continue
            if not exists(dirname(dst)):
                self.logger.debug('"{0}" created.'.format(dirname(dst)))
                if not kwargs["test"]:
                    os.makedirs(dirname(dst))
            self.logger.debug('Source     : "{0}"'.format(src))
            self.logger.debug('Destination: "{0}"'.format(dst))
            if not kwargs["test"]:
                shutil.copy2(src=src, dst=dst)
                self.logger.debug("Source copied.")

    def insert(self, index, value):
        self._seq.insert(index, value)


# ================
# Initializations.
# ================
arguments = parser.parse_args()
filestocopy = CopyFilesFrom(arguments.file)


# ========
# Logging.
# ========
with open(os.path.join(os.path.expandvars("%_COMPUTING%"), "logging.yml")) as fp:
    dictConfig(yaml.load(fp))
logger = logging.getLogger(os.path.splitext(os.path.basename(__file__))[0])
logger.debug("Delay: {0} second(s).".format(arguments.delay))
logger.debug("{0:>5d} file(s) to copy.".format(len(filestocopy)))


# ===============
# Main algorithm.
# ===============
if len(filestocopy):

    # Mise � jour imm�diate.
    if not arguments.delay:
        filestocopy(test=arguments.test)
        sys.exit(0)

    # Mise � jour diff�r�e.
    s = sched.scheduler()
    s.enter(arguments.delay, 1, filestocopy, kwargs={"test": arguments.test})
    s.run()
