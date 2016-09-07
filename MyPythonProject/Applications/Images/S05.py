# -*- coding: ISO-8859-1 -*-
import os
from collections import Counter
from operator import itemgetter
from Applications import shared

__author__ = 'Xavier ROSSET'


src = r"G:\Videos\Samsung S5"
# print(reflist)
# tzinfos = {"CET": tz.gettz("Europe/Paris"), "CEST": tz.gettz("Europe/Paris")}
# print([(a, timezone("Europe/Paris").localize(b).timestamp()*1000 + c) for
       # a, b, c in [(itemgetter(0)(i), parser.parse("{0}{1}".format(itemgetter(1)(i), itemgetter(2)(i)), tzinfos=tzinfos), itemgetter(3)(i))
             # for i in sorted(sorted(sorted(map(GetImageData(pattern), ["20160527_095934.jpg", r"20160304_101202(0).jpg", r"20160304_101202.jpg"]), key=itemgetter(3)), key=itemgetter(2)), key=itemgetter(1)) if itemgetter(0)]])
# files = os.listdir()
# for item in [(fil, timestamp) for fil, timestamp in map(ImageData(pattern), files, repeat(timezone("Europe/Paris"))) if fil]:
#     os.rename(src=itemgetter(0)(item), dst=src=itemgetter(1)(item))

reflist = list()
rejected = list()
for fil in shared.filesinfolder(["jpg"], folder=src):
    try:
        obj = shared.SamsungS5(fil)
    except shared.ExifError:
        rejected.append(fil)
    else:
        reflist.append((fil, obj))
months = ["{0}{1}".format(itemgetter(1)(i).originalyear, itemgetter(1)(i).originalmonth) for i in reflist if itemgetter(1)(i).match]
files = [(os.path.basename(itemgetter(0)(i)), itemgetter(1)(i).timestamp) for i in reflist if itemgetter(1)(i).match]
print(months)
print(files)
c = Counter(months)
print(c)
print(list(c))
print(sum(c.values()))
print(rejected)
