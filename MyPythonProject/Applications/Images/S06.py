# -*- coding: ISO-8859-1 -*-
from operator import itemgetter
from collections import Counter
from itertools import count
from Applications import shared

__author__ = 'Xavier ROSSET'


x = [("file1", 1234567890), ("file2", 1234567890), ("file3", 1234567891), ("file4", 1234567892), ("file5", 1234567893), ("file6", 1234567893), ("file7", 1234567890)]
c = Counter([itemgetter(1)(i) for i in x])
y = [key for key in sorted(list(c)) if c[key] > 1]
z1 = [(itemgetter(0)(i), itemgetter(1)(i)*1000) for i in sorted(sorted(x, key=itemgetter(0)), key=itemgetter(1)) if itemgetter(1)(i) not in y]

for key in y:
    l1 = [itemgetter(0)(i) for i in sorted(sorted(x, key=itemgetter(0)), key=itemgetter(1)) if itemgetter(1)(i) == key]  # ["file1", "file2", "file3"]
    l2 = list(zip(l1, count(key*1000)))  # [("file1", 1234567890000), ("file2", 1234567890001), ("file3", 1234567890002)]
    z1 += l2

print(sorted(z1, key=itemgetter(1)))


obj = shared.Images(r"H:\201005\201005_00400.jpg")
print(sorted(obj.exif.keys()))
print(obj.exif[37500])
print(obj.exif[37520])
print(obj.exif[37521])

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
    os.rename(src=itemgetter(0)(i), dst=itemgetter(1)(i))

print(obj.exif[37522])

