# -*- coding: ISO-8859-1 -*-
from operator import itemgetter
import re

__author__ = 'Xavier ROSSET'


class MyClass1(object):

    def __init__(self, seq):

        def f1(s):
            return int(s.split(".")[0])

        def f2(s):
            return int(s.split(".")[1])

        self._index1 = 0
        self._index2 = 0
        self._seq = sorted(sorted(seq, key=f1), key=f2)

    def __call__(self):
        self._index1 += 1
        return self._seq[self._index1 - 1][2:6]
    
    def __iter__(self):
        return self

    def __next__(self):
        if self._index2 == len(self._seq):
            raise StopIteration
        self._index2 += 1
        return self._seq[self._index2 - 1][2:6]


class MyClass2(object):

    def __init__(self, seq):
        self._index1 = 0
        self._index2 = 0
        self._seq = list()
        self.seq = seq

    @property
    def seq(self):
        return self._seq

    @seq.setter
    def seq(self, arg):
        self._seq = arg

    def __call__(self):
        self._index1 += 1
        return int(re.split(r"\D+", self.seq[self._index1 - 1])[1])

    def __iter__(self):
        return self

    def __next__(self):
        if self._index2 == len(self.seq):
            raise StopIteration
        self._index2 += 1
        return self.seq[self._index2 - 1]


def func(d):
    return "201601_{0:0>5d}".format(d)


def func2(s):
    return int(re.split(r"\D+", s)[1])


x = MyClass1(["2.20160125.13", "2.20160201.13", "2.20160120.13", "1.20160625.13", "2.20160422.13", "1.20160422.13", "2.19841102.13", "2.19990822.13", "2.20021014.13", "2.20000823.13", "2.20170101.13"])
print(list(x))
print(list(iter(x, "2016")))

z1 = list(map(func, range(1, 101)))
z2, z3 = MyClass2(z1), list()
for i in iter(z2, 11):
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
