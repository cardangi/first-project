# -*- coding: ISO-8859-1 -*-
from contextlib import contextmanager
from operator import itemgetter
from functools import partial
from shutil import copytree
import os
import re
from .. import shared

__author__ = 'Xavier ROSSET'


# ==========
# Functions.
# ==========
def chgcurdir(d):
    wcdir = os.getcwd()
    os.chdir(d)
    yield
    os.chdir(wcdir)


def graboriginalmonth(s, rex):
    return s, rex.match(s)


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


# ==================
# Initializations 1.
# ==================
src = r"G:\Computing\Vidéos\Samsung S5"
pattern = r"^({0}{1})({2})\B_\B(\d{{6}})(?:\(\d\))?\.jpg$".format(shared.DFTYEARREGEX, shared.DFTMONTHREGEX, shared.DFTDAYREGEX)


# ====================
# Regular expressions.
# ====================
regex = re.compile(pattern, re.IGNORECASE)


# ==================
# Initializations 2.
# ==================
graboriginalmonth = partial(graboriginalmonth, rex=regex)


# ===============
# Main algorithm.
# ===============
reflist = [(fil, obj.group(1)) for fil, obj in map(graboriginalmonth, list(shared.filesinfolder(["jpg"], folder=src))) if obj]
for month in set([itemgetter(1)(item) for item in reflist]):
    dst = os.path.join(r"H:\\", month)
    if not os.path.exists(dst):
        copytree(src, dst, ignore=IgnoreBut(r"^{0}{1}\B_\B\d{{6}}(?:\(\d\))?\.jpg$".format(month, shared.DFTDAYREGEX)))
        with chgcurdir(dst):
            for file in os.listdir(dst):
                os.rename(file, dateutil.parse(file).timestamp())
