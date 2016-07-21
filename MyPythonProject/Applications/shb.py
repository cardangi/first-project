# -*- coding: ISO-8859-1 -*-
__author__ = 'Xavier ROSSET'

from collections import MutableMapping
from itertools import islice


class MyDict(MutableMapping):

    def __init__(self, *args, **kwargs):
        self.store = dict()
        self.update(dict(*args, **kwargs))

    def __len__(self):
        return len(self.store)

    def __getitem__(self, item):
        return self.store[self.__toto__(item)]

    def __setitem__(self, key, value):
        self.store[self.__toto__(key)] = value

    def __iter__(self):
        return iter(self.store)

    def __delitem__(self, key):
        del self.store[self.__toto__(key)]

    def __toto__(self, key):
        return "{0}xx".format(key)


# x = MyDict([("toto", "titi")], tata=15)
# print(x["toto"])
# print(x["tata"])
# print(list(x.keys()))
# for key in iter(x):
#     print(key)


x = ["1", "2", "3", "4", "5", "6"]
for i in islice(x, 4):
    print(i)
for i in islice(x, 0, 1):
    print(i)

