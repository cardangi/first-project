# -*- coding: ISO-8859-1 -*-
from collections import namedtuple
from functools import wraps
import itertools
import re

__author__ = 'Xavier ROSSET'


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


def grabdiscnumber(fil, rex):
    Disc = namedtuple("Disc", ["found", "number"])
    match = rex.search(fil)
    if match:
        return Disc(True, match.group(1))
    return Disc(False, None)


def getfilefromindex(indexes, files):
    """
    :param indexes: string only composed of digits separated by both a comma and a space ("1, 2, 3").
    :param files: files list.
    :return: list of corresponding files.
    """
    indexes_list = []
    match = re.match(r"^(\d\d?,\s)*(\d\d?)$", indexes)
    if match:
        indexes_list = indexes.split(", ")
    return [files[int(i) - 1] for i in indexes_list if int(i) <= len(files)]


def myfunction(start, end):
    """Docstring"""
    for i in range(start, end):
        yield i


def formatindexes(indexes):

    # Constants.
    SEP = ", "

    # Regular expressions.
    rex1 = re.compile(r"^\d\d?$")
    rex2 = re.compile(r"^\d\d?\-\d\d?$")

    # Algorithm.
    if any([rex1.match(index) or rex2.match(index) for index in indexes.split(SEP)]):
        out1 = [index for index in indexes.split(SEP) if rex1.match(index)]
        out2 = list(itertools.chain.from_iterable([map(str, i) for i in [list(i) for i in [i(myfunction)() for i in map(Decorator, [index for index in indexes.split(SEP) if rex2.match(index)])]]]))
        return sorted(set(out1 + out2), key=int)
    return []


# aaaaaaaaaaaaaaa



