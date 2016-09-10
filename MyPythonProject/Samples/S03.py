# -*- coding: ISO-8859-1 -*-
__author__ = 'Xavier ROSSET'


def myfunc1(s):
    return int(s.split("_")[1])


def myfunc2(s):
    return int(s.split("_")[0])


x = ["2016_00001", "2016_00002", "2016_00003", "2016_00101", "2015_00456"]
print(int(max(x).split("_")[1]))
print(int(max([i.split("_")[1] for i in x])))
print(sorted(x, key=myfunc1))
print(sorted(sorted(x, key=myfunc1), key=myfunc2))
