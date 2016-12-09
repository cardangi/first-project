# -*- coding: utf-8 -*-
from collections import namedtuple, MutableSequence
from itertools import accumulate, repeat
from contextlib import contextmanager
from logging.config import dictConfig
from Applications import shared
from operator import itemgetter
import argparse
import logging
import glob
import yaml
import sys
import os
import re

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
        images = {k: v for k, v in dict(self.func3(psarg)).items() if v}
        months = sorted(list(images), key=int)
        totals = sorted(accumulate(self.func1(self.func2(images))))
        totals.insert(0, 1)
        self._collection = list(zip(months, map(list, self.func0(totals))))

    @staticmethod
    def func3(m):
        """
        Return [("201001", ["file", "file2", "file3"]), ("201002", ["file", "file2", "file3"])]
        :param m: month.
        :return: files grouped by month.
        """
        return [(month, list(glob.iglob(os.path.normpath(os.path.join(shared.IMAGES, month, r"*.jpg"))))) for month in ("{0}{1:0>2}".format(m, i) for i in range(1, 13))]

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
    def index(self, arg):
        self._index = arg

    def __call__(self, *args, **kwargs):
        self.index += 1
        return '{index:>4d}. Rename "{src}" to "{dst}".'.format(index=self.index, src=kwargs["src"], dst=kwargs["dst"])


# ==========
# Functions.
# ==========
@contextmanager
def decorator(obj, s):
    sep = "".join(list(repeat("-", len(s))))
    obj.info(sep)
    yield
    obj.info(sep)


@contextmanager
def rename(src, dst, test=True, obj=None, message=None):
    failed, results = False, {True: "Failed", False: "Succeeded"}
    if not test:
        try:
            os.rename(src=src, dst=dst)
        except OSError as err:
            failed = True
            if obj:
                obj.exception(err)
    yield failed
    if message and obj:
        obj.info("{log} {result}.".format(log=message, result=results[failed]))


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


# =================
# Arguments parser.
# =================
parser = argparse.ArgumentParser()
parser.add_argument("year", type=year, nargs="+")
parser.add_argument("-t", "--test", action="store_true")


# ==========
# Constants.
# ==========
MODES = {True: "test mode.", False: "rename mode."}


# ================
# Initializations.
# ================
status, nt, results, log, arguments = 99, namedtuple("nt", "match sequence"), [], Log(), parser.parse_args()


# ========
# Logging.
# ========
with open(os.path.join(os.path.expandvars("%_COMPUTING%"), "logging.yml"), encoding=shared.UTF8) as fp:
    dictConfig(yaml.load(fp))
logger = logging.getLogger("Images.{0}".format(os.path.splitext(os.path.basename(__file__))[0]))
logger.info(MODES[arguments.test].upper())


# ===============
# Main algorithm.
# ===============
for year in arguments.year:
    try:
        collection = ImagesCollection(year)
    except ValueError as exception:
        logger.exception("Value error: {0}.".format(exception))
    else:
        for keys, values in collection:
            curdir = os.path.normpath(os.path.join(shared.IMAGES, keys))
            files = sorted(glob.glob(os.path.normpath(os.path.join(shared.IMAGES, keys, r"*.jpg"))))
            args = zip(map(os.path.basename, files), map(func2, files), map(func3, repeat(keys), values))

            #    -------------------------------------------------------------------
            # 1. Tous les fichiers du répertoire répondent au masque "CCYYMM_xxxxx".
            #    -------------------------------------------------------------------
            if all(i.match for i in map(func1, map(os.path.basename, files))):
                try:
                    assert [int(i.sequence) for i in map(func1, map(os.path.basename, files))] == values
                except AssertionError:
                    msg = '"{0}": renaming needed.'.format(curdir)
                    with decorator(logger, msg):
                        logger.info(msg)
                    with shared.chgcurdir(curdir):

                        log.index = 0
                        for arg in args:
                            with rename(itemgetter(0)(arg), itemgetter(1)(arg), obj=logger, message=log(itemgetter(0)(arg), itemgetter(1)(arg)), test=arguments.test) as result:
                                results.append(result)

                        log.index = 0
                        for arg in args:
                            with rename(itemgetter(1)(arg), itemgetter(2)(arg), obj=logger, message=log(itemgetter(1)(arg), itemgetter(2)(arg)), test=arguments.test) as result:
                                results.append(result)

                    continue

                msg = '"{0}": no renaming needed.'.format(curdir)
                with decorator(logger, msg):
                    logger.info(msg)
                continue

            #    ---------------------------------------------------------------
            # 2. Aucun fichier du répertoire ne répond au masque "CCYYMM_xxxxx".
            #    ---------------------------------------------------------------
            if all(not i.match for i in map(func1, map(os.path.basename, files))):
                msg = '"{0}": renaming needed.'.format(curdir)
                with decorator(logger, msg):
                    logger.info(msg)
                with shared.chgcurdir(curdir):
                    log.index = 0
                    for arg in args:
                        with rename(itemgetter(0)(arg), itemgetter(2)(arg), obj=logger, message=log(itemgetter(0)(arg), itemgetter(2)(arg)), test=arguments.test) as result:
                            results.append(result)
                continue

            #    ------------------------------------------------------------------
            # 3. Au moins un fichier du répertoire répond au masque "CCYYMM_xxxxx".
            #    ------------------------------------------------------------------
            msg = '"{0}": renaming needed.'.format(curdir)
            with decorator(logger, msg):
                logger.info(msg)
            with shared.chgcurdir(curdir):

                log.index = 0
                for arg in args:
                    with rename(itemgetter(0)(arg), itemgetter(1)(arg), obj=logger, message=log(itemgetter(0)(arg), itemgetter(1)(arg)), test=arguments.test) as result:
                        results.append(result)

                log.index = 0
                for arg in args:
                    with rename(itemgetter(1)(arg), itemgetter(2)(arg), obj=logger, message=log(itemgetter(1)(arg), itemgetter(2)(arg)), test=arguments.test) as result:
                        results.append(result)

            continue


# ===============
# Exit algorithm.
# ===============
if not arguments.test:
    if all(results):
        status = 0
    sys.exit(status)
sys.exit(0)
