# -*- coding: ISO-8859-1 -*-
from collections import namedtuple

__author__ = 'Xavier ROSSET'


def grabdiscnumber(fil, rex):
    Disc = namedtuple("Disc", ["found", "number"])
    match = rex.search(fil)
    if match:
        return Disc(True, match.group(1))
    return Disc(False, None)
