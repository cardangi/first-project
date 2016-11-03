# -*- coding: ISO-8859-1 -*-
from collections import MutableSequence
from mutagen import File, MutagenError
from contextlib import ExitStack
import argparse
import logging
import shutil
import sched
import os
import re
from .. import shared

__author__ = 'Xavier ROSSET'


# ============
# Local names.
# ============
dirname, basename, exists, normpath = os.path.dirname, os.path.basename, os.path.exists, os.path.normpath


# ==========
# Functions.
# ==========
def validdirectory(d):
    if not exists(d):
        raise argparse.ArgumentTypeError('"{0}" isn\'t a valid output directory.'.format(d))
    return d


# =================
# Arguments parser.
# =================
parser = argparse.ArgumentParser()
parser.add_argument("directory", type=validdirectory)
parser.add_argument("delay", type=int)
parser.add_argument("-t", "--test", action="store_true")


# ==========
# Constants.
# ==========
SOURCE = r"F:\\`X5"


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
class FLACFilesFrom(MutableSequence):

    def __init__(self, folder):
        self._folder = normpath(folder)
        self._regex = re.compile(r"^{0}".format(folder), re.IGNORECASE)
        self._seq = []
        for fil in shared.filesinfolder(folder=normpath(folder)):
            try:
                audio = File(fil)
            except MutagenError:
                continue
            if "audio/flac" in audio.mime:
                self._seq.append(normpath(fil))

    def __getitem__(self, item):
        return self._seq[item]

    def __setitem__(self, key, value):
        self._seq[key] = value

    def __delitem__(self, key):
        del self._seq[key]

    def __len__(self):
        return len(self._seq)

    def __call__(self, *args, **kwargs):
        stack = ExitStack()
        stack.callback(shutil.rmtree, self._folder)
        with stack:
            for fil in self:
                dst = normpath(dirname(self._regex.sub(kwargs["directory"], fil)))
                if kwargs["test"]:
                    self.log(fil, dst)
                    continue
                if not exists(dst):
                    os.makedirs(dst)
                    logger.debug('"{0}" created'.format(dst))
                shutil.copy2(src=fil, dst=dst)
                self.log(fil, dst)

    def insert(self, index, value):
        self._seq.insert(index, value)

    @staticmethod
    def log(arg1, arg2):
        logger.debug("Copy file.")
        logger.debug("\tSource\t\t: {0}".format(arg1).expandtabs(3))
        logger.debug("\tDestination : {0}".format(arg2).expandtabs(3))


# ===============
# Main algorithm.
# ===============
s = sched.scheduler()
s.enter(arguments.delay, 1, FLACFilesFrom(SOURCE), kwargs={"directory": arguments.directory, "test": arguments.test})
s.run()
