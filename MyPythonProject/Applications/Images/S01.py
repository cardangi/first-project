# -*- coding: ISO-8859-1 -*-
import re
import os
from Applications import shared as s1

__author__ = 'Xavier ROSSET'


def prefix(path):
    match = re.match("^(\d{8})\B_\B(\d{6})(?:\((\d)\))?\.jpg$", path)
    if match:
        print(len(match.groups()))
        if len(match.groups()) == 2:
            return int("{0}{1}0".format(match.group(1), match.group(2)))
        if len(match.groups()) == 3:
            return int("{0}{1}{2}".format(match.group(1), match.group(2), int(match.group(3)) + 1))


l, d1, d2 = [], {}, {}
for fil in s1.filesinfolder(["jpg"], r"G:\Videos\Samsung S5"):
    try:
        img = s1.Images(fil)
    except (s1.ExifError, OSError):
        pass
    else:
        # print("{0}: {1}{2}".format(fil, img.originalyear, img.originalmonth))
        # l.append(fil)
        key = "{0}{1}".format(img.originalyear, img.originalmonth)
        d1[key] = d1.get(key, 0) + 1
        if key not in d2:
            d2[key] = list()
        d2[key].append(os.path.basename(fil))
print(d1)
for key in d2.keys():
    d2[key] = sorted(d2[key], key=prefix)
print(d2)

