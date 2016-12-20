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
class Interface(object):

    _regex = re.compile(r"(?:{0})".format(shared.DFTYEARREGEX))
    _inputs = [("Would you like to run test Mode? [Y/N]", "test"), ("Please enter year", "year")]
    year = shared.Year()

    def __init__(self):
        self._index, self._step = 0, 0
        self._year = None
        self._test = None
        self._arguments = []

    def __iter__(self):
        return self

    def __next__(self):
        if self._index >= len(self._inputs):
            raise StopIteration
        self._index += 1
        self._step += 1
        return self._inputs[self._index - 1]

    # -----
    # STEP.
    # -----
    @property
    def step(self):
        return self._step

    # ----------
    # ARGUMENTS.
    # ----------
    @property
    def arguments(self):
        return self._arguments

    # -----
    # YEAR.
    # -----
    # @property
    # def year(self):
    #     return self._year
    #
    # @year.setter
    # def year(self, arg):
    #     value = self._regex.findall(arg)
    #     if not value:
    #         raise ValueError("Please enter coherent year(s).")
    #     self._year = value
    #     self._arguments.extend(value)

    # -----
    # TEST.
    # -----
    @property
    def test(self):
        return self._test

    @test.setter
    def test(self, arg):
        if arg not in shared.ACCEPTEDANSWERS:
            raise ValueError("Please enter coherent answer.")
        self._test = arg
        if arg.upper() == "Y":
            self._arguments.append("--test")


class ImagesCollection(MutableSequence):

    def __init__(self, year):
        self._collection = None
        self.collection = year

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
    def collection(self, arg):

        # Argument must be a coherent year.
        if not re.match(r"^(?=\d{4})20[0-2]\d$", str(arg)):
            raise ValueError('"{0}" is not a valid year'.format(arg))

        # Dictionary of images grouped by month.
        # Example: {"201001": ["file", "file2", "file3"], "201002": ["file", "file2", "file3"]}
        images = {k: v for k, v in dict(self.func3(arg)).items() if v}

        # List of found months.
        # Example: ["201001", "201002"]
        months = sorted(images, key=int)

        # List of accumulated counts.
        # Example: [100", 145]
        counts = [1]
        counts.extend(sorted(accumulate(self.func1(self.func2(images)))))

        # List of accumulated counts grouped by months.
        # Example: [("201001", 100), ("201002", 145)]
        self._collection = list(zip(months, map(list, self.func0(counts))))

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
        return {k: len(v) for k, v in d.items()}

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

    def __call__(self, **kwargs):
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
    failed, result = False, {True: "Failed", False: "Succeeded"}
    if not test:
        try:
            os.rename(src=src, dst=dst)
        except OSError as err:
            failed = True
            if obj:
                obj.exception(err)
    yield failed
    if message and obj:
        obj.info("{log} {result}.".format(log=message, result=result[failed]))


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


# ===============
# Main algorithm.
# ===============
if __name__ == "__main__":

    # --> Constants.
    MODES = {True: "test mode.", False: "rename mode."}

    # --> Initializations.
    status, nt, results, log = 99, namedtuple("nt", "match sequence"), [], Log()

    # --> Logging.
    with open(os.path.join(os.path.expandvars("%_COMPUTING%"), "logging.yml"), encoding="UTF_8") as fp:
        dictConfig(yaml.load(fp))
    logger = logging.getLogger("Images.{0}".format(os.path.splitext(os.path.basename(__file__))[0]))

    # --> User interface.
    gui = shared.interface(Interface())

    # --> Parse arguments.
    # arguments = parser.parse_args(gui.arguments)

    # --> Log arguments.
    logger.debug(gui.test)
    logger.debug(gui.year)

    sys.exit()

    # --> Main algorithm.
    for year in arguments.year:
        try:
            collection = ImagesCollection(year)
        except ValueError as err:
            logger.exception(err)
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

    # --> Exit algorithm.
    if not arguments.test:
        if all(results):
            status = 0
        sys.exit(status)
    sys.exit(0)
