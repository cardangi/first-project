# -*- coding: ISO-8859-1 -*-
from operator import eq, lt, gt

__author__ = 'Xavier ROSSET'


def myfunc1(lst):
    return all([lt(x, 50) for x in lst])


def myfunc2(lst):
    return all([gt(x, 50) for x in lst])


def myfunc3(lst):
    return any([gt(x, 5) for x in lst])


def myfunc4(lst):
    return any([eq(x, 5) for x in lst])


def myfunc5(lst):
    return all([eq(x, 5) for x in lst])


assert myfunc1([1, 2, 3, 4, 5, 6, 7, 8]) is True
assert myfunc2([1, 2, 3, 4, 5, 6, 7, 8]) is False
assert myfunc3([1, 2, 3, 4, 5, 6, 7, 8]) is True
assert myfunc4([1, 2, 3, 4, 5, 6, 7, 8]) is True
assert myfunc5([1, 2, 3, 4, 5, 6, 7, 8]) is False
