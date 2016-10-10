# -*- coding: ISO-8859-1 -*-
from collections import namedtuple, MutableSequence
from itertools import accumulate, repeat
from contextlib import contextmanager
from operator import itemgetter
from datetime import datetime
from pytz import timezone
import argparse
import logging
import glob
import sys
import os
import re
from .. import shared

__author__ = 'Xavier ROSSET'


# ========
# Classes.
# ========
class ImagesCollection(MutableSequence):

    def __init__(self, ccyy):
        self._collection = list()
        self.collection = ccyy

    def __getitem__(self, item):
        return self.collection[item]

    def __setitem__(self, key, value):
        self.collection[key] = value

    def __delitem__(self, key):
        del self.collection[key]

    def __len__(self):
        return len(self.collection)

    def insert(self, index, value):
        self.collection.insert(index, value)

    @property
    def collection(self):
        return self._collection

    @collection.setter
    def collection(self, psarg):
        value = str(psarg)
        if not re.match(r"^(?=\d{4})20[0-2]\d$", value):
            raise ValueError('"{0}" is not a valid year'.format(psarg))
        months = sorted(dict(self.func3(psarg)).keys(), key=int)
        totals = sorted(accumulate(self.func1(self.func2(dict(self.func3(psarg))))))
        totals.insert(0, 1)
        self._collection = list(zip(months, map(list, self.func0(totals))))

    @staticmethod
    def func3(m):
        """
        Return [("201001", ["file", "file2", "file3"]), ("201002", ["file", "file2", "file3"])]
        :param m: month.
        :return: files grouped by month.
        """
        collection = list()
        for i in range(1, 13):
            month = "{0}{1:0>2}".format(m, i)
            if os.path.exists(os.path.normpath(os.path.join(r"h:\\", month))):
                collection.append((month, list(glob.iglob(os.path.normpath(os.path.join(r"h:\\", month, r"*.jpg"))))))
        return collection

    @staticmethod
    def func2(d):
        """
        Return {"201001": 100, "201002": 200}.
        :param d: dictionnary of files grouped by month.
        :return: counts by month.
        """
        return {k: len(d[k]) for k in list(d)}

    @staticmethod
    def func1(d):
        """
        Return [1, 100, 200].
        :param d: dictionnary of files grouped by month.
        :return: counts list.
        """
        return [d[k] for k in sorted(d, key=int)]

    @staticmethod
    def func0(l):
        it = iter(l)
        i = next(it, False)
        while i:
            j = next(it, False)
            if not j:
                break
            yield range(i, j + 1)
            i = j + 1


class Log(object):

    def __init__(self, index=0):
        self._index = 0
        self.index = index

    @property
    def index(self):
        return self._index

    @index.setter
    def index(self, psarg):
        self._index = psarg

    def __call__(self, src, dst):
        self.index += 1
        return '{index:>4d}. Rename "{src}" to "{dst}".'.format(index=self.index, src=src, dst=dst)


# ==========
# Functions.
# ==========
@contextmanager
def logdecorator(s):
    sep = "".join(list(repeat("-", len(s))))
    logger.info(sep)
    yield
    logger.info(sep)


def year(y):
    import re
    regex = re.compile(r"^(?=\d{4})20[0-2]\d$")
    if not regex.match(y):
        raise argparse.ArgumentTypeError('"{0}" is not a valid year'.format(y))
    return y


def func1(s):
    match = re.match(r"(?i)^\d{6}\B_\B(\d{5})\.jpg", s)
    if match:
        return nt(True, match.group(1))
    return nt(False, None)


def func2(s):
    return "ren_{0}".format(os.path.basename(s))


def func3(s, i):
    return "{0}_{1:0>5d}.jpg".format(s, i)


def rename(src, dst):
    try:
        os.rename(src=src, dst=dst)
    except OSError:
        return True
    else:
        return False


# ========
# Logging.
# ========
logger = logging.getLogger("%s.%s" % (__package__, os.path.basename(__file__)))


# =================
# Arguments parser.
# =================
parser = argparse.ArgumentParser()
parser.add_argument("year", type=year, nargs="+")
parser.add_argument("-t", "--test", action="store_true")


# ==========
# Constants.
# ==========
RESULTS, MODES = {True: "Failed", False: "Succeeded"}, {True: "test mode.", False: "rename mode."}


# ================
# Initializations.
# ================
status, nt, results, log, arguments = 99, namedtuple("nt", "match sequence"), [], Log(), parser.parse_args()


# ==============
# Start logging.
# ==============
logger.info("{0:=^140s}".format(" {0} ".format(shared.dateformat(datetime.now(tz=timezone(shared.DFTTIMEZONE)), shared.TEMPLATE1))))
logger.info('START "%s".' % (os.path.basename(__file__),))
logger.info(MODES[arguments.test].upper())


# ===============
# Main algorithm.
# ===============
for year in arguments.year:
    try:
        collection = ImagesCollection(year)
    except ValueError as exception:
        logger.info("Value error: {0}.".format(exception))
    else:
        for keys, values in collection:
            curdir = os.path.normpath(os.path.join(r"h:\\", keys))
            files = sorted(glob.glob(os.path.normpath(os.path.join(r"h:\\", keys, r"*.jpg"))))
            args = list(zip(map(os.path.basename, files), map(func2, files), map(func3, repeat(keys), values)))

            #    -------------------------------------------------------------------
            # 1. Tous les fichiers du répertoire répondent au masque "CCYYMM_xxxxx".
            #    -------------------------------------------------------------------
            if all([i.match for i in map(func1, map(os.path.basename, files))]):
                try:
                    assert [int(i.sequence) for i in map(func1, map(os.path.basename, files))] == values
                except AssertionError:
                    msg = '"{0}": renaming needed.'.format(curdir)
                    with logdecorator(msg):
                        logger.info(msg)
                    with shared.chgcurdir(curdir):

                        log.index = 0
                        for arg in args:
                            msg = log(src=itemgetter(0)(arg), dst=itemgetter(1)(arg))
                            if not arguments.test:
                                result = rename(src=itemgetter(0)(arg), dst=itemgetter(1)(arg))
                                results.append(result)
                                msg = "{log} {result}.".format(log=msg, result=RESULTS[result])
                            logger.info(msg)

                        log.index = 0
                        for arg in args:
                            msg = log(src=itemgetter(1)(arg), dst=itemgetter(2)(arg))
                            if not arguments.test:
                                result = rename(src=itemgetter(1)(arg), dst=itemgetter(2)(arg))
                                results.append(result)
                                msg = "{log} {result}.".format(log=msg, result=RESULTS[result])
                            logger.info(msg)

                    continue

                msg = '"{0}": no renaming needed.'.format(curdir)
                with logdecorator(msg):
                    logger.info(msg)
                continue

            #    ---------------------------------------------------------------
            # 2. Aucun fichier du répertoire ne répond au masque "CCYYMM_xxxxx".
            #    ---------------------------------------------------------------
            if all([not i.match for i in map(func1, map(os.path.basename, files))]):
                msg = '"{0}": renaming needed.'.format(curdir)
                with logdecorator(msg):
                    logger.info(msg)
                with shared.chgcurdir(curdir):
                    log.index = 0
                    for arg in args:
                        msg = log(src=itemgetter(0)(arg), dst=itemgetter(2)(arg))
                        if not arguments.test:
                            result = rename(src=itemgetter(0)(arg), dst=itemgetter(2)(arg))
                            results.append(result)
                            msg = "{log} {result}.".format(log=msg, result=RESULTS[result])
                        logger.info(msg)
                continue

            #    ------------------------------------------------------------------
            # 3. Au moins un fichier du répertoire répond au masque "CCYYMM_xxxxx".
            #    ------------------------------------------------------------------
            msg = '"{0}": renaming needed.'.format(curdir)
            with logdecorator(msg):
                logger.info(msg)
            with shared.chgcurdir(curdir):

                log.index = 0
                for arg in args:
                    msg = log(src=itemgetter(0)(arg), dst=itemgetter(1)(arg))
                    if not arguments.test:
                        result = rename(src=itemgetter(0)(arg), dst=itemgetter(1)(arg))
                        results.append(result)
                        msg = "{log} {result}.".format(log=msg, result=RESULTS[result])
                    logger.info(msg)

                log.index = 0
                for arg in args:
                    msg = log(src=itemgetter(1)(arg), dst=itemgetter(2)(arg))
                    if not arguments.test:
                        result = rename(src=itemgetter(1)(arg), dst=itemgetter(2)(arg))
                        results.append(result)
                        msg = "{log} {result}.".format(log=msg, result=RESULTS[result])
                    logger.info(msg)

            continue


# =============
# Stop logging.
# =============
logger.info('END "%s".' % (os.path.basename(__file__),))


# ===============
# Exit algorithm.
# ===============
if not arguments.test:
    if all(results):
        status = 0
    sys.exit(status)
sys.exit(0)
