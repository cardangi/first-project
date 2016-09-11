# -*- coding: ISO-8859-1 -*-
from itertools import accumulate
from collections import namedtuple
import glob
import os
import re

__author__ = 'Xavier ROSSET'


blabla = namedtuple("blabla", "match sequence")


class Toto(object):

    def __init__(self, year):
        self._index = 0
        self.toto = dict()
        for i in range(1, 13):
            month = "{0}{1:0>2}".format(year, i)
            if os.path.exists(os.path.normpath(os.path.join(r"H:\\", month))):
                self.toto[month] = glob.glob(os.path.normpath(os.path.join(r"H:\\", month, r"*.jpg")))  # {"201001": ["file1", "file2"], 201002": ["file1", "file2"]}
        self.titi = {key: len(self.toto[key]) for key in self.toto.keys()}  # {"201001": 100, 201002": 15}
        self.titi1 = [self.titi[key] for key in sorted(self.titi.keys())]  # [100, 15, 45]
        self.tata = list(accumulate(self.titi1))  # [100, 115, 160]
        self.tutu = {key: self.__next__() for key in sorted(self.toto.keys())}  # {"201001": [1, 2, 3, 4], "201002": [5, 6, 7, 8, 9, 10], "201003": [11, 12, 13, 14, 15]}

    def __iter__(self):
        return self

    def __next__(self):
        self._index += 1
        if self._index > len(self.tata):
            raise StopIteration
        if self._index == 1:
            return list(range(self._index, self.tata[self._index - 1] + 1))
        return list(range(self.tata[self._index - 2] + 1, self.tata[self._index - 1] + 1))


def func(s):
    match = re.match(r"(?i)^\d{6}\B_\B(\d{5})\.jpg", s)
    if match:
        return blabla(True, match.group(1))
    return blabla(False, None)


for x in map(Toto, ["2010", "2016"]):
    for key in sorted(x.toto.keys()):
        z = [int(i.sequence) for i in map(func, map(os.path.basename, sorted(x.toto[key]))) if i.match]
        try:
            assert z == x.tutu[key]
        except AssertionError:
            print(key, "KO")
        else:
            print(key, "OK")
