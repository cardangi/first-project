# -*- coding: ISO-8859-1 -*-
from collections import MutableSequence
from operator import itemgetter
import re

__author__ = 'Xavier ROSSET'


class MyClass1(MutableSequence):

    def __init__(self, seq):
        self._index = 0
        self._seq = sorted(sorted(seq, key=self.f1), key=self.f2)

    def __getitem__(self, item):
        return self._seq[item]

    def __setitem__(self, key, value):
        self._seq[key] = value

    def __delitem__(self, key):
        del self._seq[key]

    def __len__(self):
        return len(self._seq)

    def __iter__(self):
        for item in self._seq:
            yield item[2:6]

    def __call__(self):
        self._index += 1
        return self._seq[self._index - 1][2:6]

    def insert(self, index, value):
        self._seq.insert(index, value)

    @staticmethod
    def f1(s):
        return int(s.split(".")[0])

    @staticmethod
    def f2(s):
        return int(s.split(".")[1])


class MyClass2(MutableSequence):

    def __init__(self, seq):
        self._index = 0
        self._seq = seq

    def __getitem__(self, item):
        return self._seq[item]

    def __setitem__(self, key, value):
        self._seq[key] = value

    def __delitem__(self, key):
        del self._seq[key]

    def __len__(self):
        return len(self._seq)

    def __call__(self):
        self._index += 1
        return int(re.split(r"\D+", self._seq[self._index - 1])[1])

    def insert(self, index, value):
        self._seq.insert(index, value)


def func(d):
    return "201601_{0:0>5d}".format(d)


def func2(s):
    return int(re.split(r"\D+", s)[1])


x = MyClass1(["2.20160125.13", "2.20160201.13", "2.20160120.13", "1.20160625.13", "2.20160422.13", "1.20160422.13", "2.19841102.13", "2.19990822.13", "2.20021014.13", "2.20000823.13", "2.20170101.13"])
print(list(x))
print(list(iter(x, "2016")))

z1 = list(map(func, range(1, 101)))
z2, z3 = MyClass2(z1), list()
for i in iter(z2, 51):
    for j in z1:
        try:
            assert func2(j) == i
        except AssertionError:
            pass
        else:
            z3.append(j)
if z3:
    for i in enumerate(z3, 1):
        print("{index:.>5d}. {image}".format(index=itemgetter(0)(i), image=itemgetter(1)(i)))
