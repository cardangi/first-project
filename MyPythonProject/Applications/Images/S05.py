# -*- coding: ISO-8859-1 -*-
import os
import re
import shutil
import logging
import argparse
from pytz import timezone
from datetime import datetime
from collections import Counter
from operator import itemgetter
from contextlib import contextmanager
from Applications import shared

__author__ = 'Xavier ROSSET'


# ========
# Logging.
# ========
logger = logging.getLogger("{0}.{1}".format(__package__, os.path.basename(__file__)))


# ========
# Classes.
# ========
class IgnoreBut(object):

    def __init__(self, *patterns):
        self._patterns = patterns

    def __call__(self, path, content):
        l = list()
        for item in content:
            for pattern in self._patterns:
                match = re.match(pattern, item)
                if match:
                    break
            else:
                l.append(item)
        return l


# ==========
# Functions.
# ==========
@contextmanager
def chgcurdir(d):
    wcdir = os.getcwd()
    if not os.path.exists(d):
        yield True
    elif os.path.exists(d):
        if not os.path.isdir(d):
            yield True
        elif os.path.isdir(d):
            os.chdir(d)
            yield False
            os.chdir(wcdir)


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
parser.add_argument("source", type=validpath)
parser.add_argument("-r", "--rename", action="store_true")
parser.add_argument("-t", "--test", action="store_true")


# ==========
# Constants.
# ==========
TABSIZE = 3


# ================
# Initializations.
# ================
included, excluded, arguments = list(), list(), parser.parse_args()


# ==============
# Log arguments.
# ==============
logger.info("{0:=^140s}".format(" {0} ".format(shared.dateformat(datetime.now(tz=timezone(shared.DFTTIMEZONE)), shared.TEMPLATE1))))
logger.info('START "{0}".'.format(os.path.basename(__file__)))
logger.debug("Source directory.")
logger.debug('\t"{0}".'.format(arguments.source).expandtabs(TABSIZE))


# ===============
# Main algorithm.
# ===============


#     ----------
#  1. Get files.
#     ----------
for fil in shared.filesinfolder(["jpg"], folder=arguments.source):
    try:
        obj = shared.SamsungS5(fil)
    except shared.ExifError:
        excluded.append(fil)
    else:
        included.append((fil, obj))


#     ---------------
#  2. Group by month.
#     ---------------
c = Counter(["{0}{1}".format(itemgetter(1)(i).originalyear, itemgetter(1)(i).originalmonth) for i in included if itemgetter(1)(i).match])


#     ---------------
#  3. Log statistics.
#     ---------------
logger.debug("{0:>4d} file(s) found.".format(sum(c.values())))
for month in sorted(list(c), key=int):
    logger.debug("\t{0}: {1:>4d} file(s).".format(month, c[month]).expandtabs(TABSIZE))


#     ----------------
#  4. Copy and rename.
#     ----------------
for month in sorted(list(c), key=int):
    included, curdir = list(), os.path.normpath(os.path.join(r"H:\\", month))
    if not os.path.exists(curdir):

        # Copy.
        logger.debug('Copy files using "shutil.copytree".')
        logger.debug('\tSource\t\t: "{0}".'.format(arguments.source).expandtabs(TABSIZE))
        logger.debug('\tDestination : "{0}".'.format(curdir).expandtabs(TABSIZE))
        logger.debug('\tFiles\t\t\t: {0:>4d} file(s) to copy.'.format(c[month]).expandtabs(TABSIZE))
        shutil.copytree(arguments.source, curdir, ignore=IgnoreBut(r"^({0})({1})\B_\B(\d{{6}})(?:\((\d)\))?\.jpg$".format(month, shared.DFTDAYREGEX)))

        # Rename.
        if arguments.rename:
            with chgcurdir(curdir) as exception:
                logger.debug("Change current working directory.")
                logger.debug('\t"{0}" set as current working directory.'.format(curdir).expandtabs(TABSIZE))
                if not exception:
                    for fil in shared.filesinfolder(["jpg"], folder=curdir):
                        try:
                            obj = shared.SamsungS5(fil)
                        except shared.ExifError:
                            pass
                        else:
                            included.append((os.path.basename(fil), obj.timestamp))
                    for src, dst in included:
                        logger.debug("Rename file.")
                        logger.debug('\tBefore: "{0}".'.format(src).expandtabs(TABSIZE))
                        logger.debug('\tAfter : "{0}.jpg".'.format(dst).expandtabs(TABSIZE))
                        if not arguments.test:
                            try:
                                os.rename(src=src, dst="{0}.jpg".format(dst))
                            except OSError:
                                logger.debug("\tRename failed.".expandtabs(4))
                            else:
                                logger.debug("\tRename succeeded.".expandtabs(4))


# ===============
# Exit algorithm.
# ===============
logger.info('END "{0}".'.format(os.path.basename(__file__)))
