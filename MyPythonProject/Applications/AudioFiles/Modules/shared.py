# -*- coding: ISO-8859-1 -*-
from collections import namedtuple
from functools import wraps
import itertools
import re

__author__ = 'Xavier ROSSET'


# ========
# Classes.
# ========
class Decorator(object):

    def __init__(self, arg):
        start, end = list(map(int, arg.split("-")))
        self._start = start
        self._end = end + 1

    def __call__(self, func):

        @wraps(func)
        def wrapper():
            return func(self._start, self._end)

        return wrapper


# ==========
# Functions.
# ==========
def grabdiscnumber(fil, rex):
    Disc = namedtuple("Disc", ["found", "number"])
    match = rex.search(fil)
    if match:
        return Disc(True, match.group(1))
    return Disc(False, None)


def getrange(start, end):
    """Docstring"""
    for i in range(start, end):
        yield i


def formatindexes(indexes):

    # Constants.
    sep = ", "

    # Regular expressions.
    rex1 = re.compile(r"^\d\d?$")
    rex2 = re.compile(r"^\d\d?\-\d\d?$")

    # Algorithm.
    if any([rex1.match(index) or rex2.match(index) for index in indexes.split(sep)]):
        out1 = [index for index in indexes.split(sep) if rex1.match(index)]
        out2 = list(itertools.chain.from_iterable([map(str, i) for i in [list(i) for i in [obj(getrange)() for obj in map(Decorator, [index for index in indexes.split(sep) if rex2.match(index)])]]]))
        return sorted(set(out1 + out2), key=int)
    return []
