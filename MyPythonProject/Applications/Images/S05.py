# -*- coding: ISO-8859-1 -*-
import os
from collections import Counter
from operator import itemgetter
from contextlib import contextmanager
from Applications import shared

__author__ = 'Xavier ROSSET'


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
        if not os.path.isidr(d):
            yield True
        elif os.path.isidr(d):
            os.chdir(d)
            yield False
            os.chdir(wcdir)


# ==========
# Constants.
# ==========
SRC = r"G:\Videos\Samsung S5"


# ================
# Initializations.
# ================
included, excluded = list(), list()


# ===============
# Main algorithm.
# ===============


#  1. Get files.
for fil in shared.imagesinfolder(["jpg"], folder=SRC):
    try:
        obj = shared.SamsungS5(fil)
    except shared.ExifError:
        excluded.append(fil)
    else:
        included.append((fil, obj))


#  2. Group by month.
c = Counter(["{0}{1}".format(itemgetter(1)(i).originalyear, itemgetter(1)(i).originalmonth) for i in included if itemgetter(1)(i).match])


#  3. Copy and rename.
for month in sorted(list(c), key=int):
    included, curdir = list(), os.path.join(r"H:\\", month)
    if not os.path.exists(curdir):

        # Copy.
        copytree(SRC, curdir, ignore=IgnoreBut(r"^({0})({1})\B_\B(\d{{6}})(?:\((\d)\))?\.jpg$".format(curdir, DFTDAYREGEX)))

        # Rename.
        with chgcurdir(curdir) as exception:
            if not exception:
                for fil in shared.imagesinfolder(["jpg"]):
                    try:
                        obj = shared.SamsungS5(fil)
                    except shared.ExifError:
                        pass
                    else:
                        included.append((fil, obj))
                for src, dst in included:
                    os.rename(src=src, dst="{0}.jpg".format(dst))
