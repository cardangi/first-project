# -*- coding: utf-8 -*-
from itertools import groupby
from operator import itemgetter

__author__ = 'Xavier ROSSET'


mylist = [("2014", "AB"), ("2010", "A"), ("2013", "B"), ("2010", "C"), ("2016", "D"), ("2015", "E"), ("2010", "F"), ("2016", "G"), ("2012", "H"), ("2012", "I"), ("2010", "J"), ("2014", "AA"), ("2015", "K")]
for k, v in groupby(sorted(sorted(mylist, key=itemgetter(1)), key=lambda i: int(i[0])), key=lambda i: int(i[0])):
    print(k, sorted([itemgetter(1)(item) for item in v]))
