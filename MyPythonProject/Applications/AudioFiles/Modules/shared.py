# -*- coding: ISO-8859-1 -*-
from collections import namedtuple
import re

__author__ = 'Xavier ROSSET'


def grabdiscnumber(fil, rex):
    Disc = namedtuple("Disc", ["found", "number"])
    match = rex.search(fil)
    if match:
        return Disc(True, match.group(1))
    return Disc(False, None)


def getfileindex(index, lst):
    l = []
    rex1 = re.compile(r"^\d{1,2}$")
    rex2 = re.compile(r"^(\d{1,2})\-(\d{1,2})$")
    for i in index.split(", "):
        match = False
        if not match:
            match = rex1.match(i)
            if match:
                i = int(i)
                if i <= len(lst):
                    l.append(i)
        if not match:
            match = rex2.match(i)
            if match:
                if int(match.group(2)) >= int(match.group(1)):
                    for j in range(int(match.group(1)), int(match.group(2))+1):
                        if j <= len(lst):
                            l.append(j)
    return sorted(l)
