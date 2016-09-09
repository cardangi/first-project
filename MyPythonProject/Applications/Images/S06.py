# -*- coding: ISO-8859-1 -*-
from collections import Counter
from operator import itemgetter
from itertools import count


class ImagesCollection(object):

    def __init__(self, collection)
        self._index = 0
        self._input = []
        self.input = collection

    def __getitem__(self, index):
        return self.output[index]

    def __iter__(self):
        return self

    def __next__(self):
        if self._index == len(self.output):
            raise StopIteration
        self._index += 1
        return self.output[self_index - 1]

    @property
    def input(self):
        return self._input

    @input.setter
    def input(self, arg):
        self._input = arg

    @property
    def counter(self):
        return Counter([itemgetter(1)(item) for item in self.input])

    @property
    def excluded(self):
        return [item for item in self.input if itemgetter(1)(item) not in self.counter]

    @property
    def included(self):
        return [key for key in self.count.keys() if self.count[key] > 1]

    @property
    def output(self):
        templist = self.excluded
        for val in self.included:
            files, timestamps, months = list(zip(*[item for item in self.input if itemgetter(1)(item) == val]))
            templist += list(zip(files, map(sum, timestamps, count(0)), months))
        return sorted(sorted(templist, key=itemgetter(0)), key=itemgetter(1))


x = ImagesCollection([("file1", 1234567890000, "201605"), ("file2", 1234567890000, "201605"), ("file3", 1234567890000, "201605"), ("file4", 1234567891000, "201605")])
for i in x:
    try:
        os.rename(src=itemgetter(0)(i), dst=itemgetter(1)(i))
    except OSError:
        pass
