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
print(obj.exif[37522])

