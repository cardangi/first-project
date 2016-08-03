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


def getfilefromindex(indexes, files):
    """
    :param indexes: string only composed of digits separated by both a comma and a space ("1, 2, 3").
    :param files: files list.
    :return: list of corresponding files.
    """
    indexes_list = []
    match = re.match(r"^(\d\d?,\s)*(\d\d?)$", indexes)
    if match:
        indexes_list = indexes.split(", ")
    return [files[int(i) - 1] for i in indexes_list if int(i) <= len(files)]


def formatindexes(indexes):
    out = []
    rex1 = re.compile(r"^\d\d?$")
    rex2 = re.compile(r"^(\d{1,2})\-(\d{1,2})$")
    for index in indexes.split(", "):
        match1 = rex1.match(index)
        match2 = rex2.match(index)
        if any([match1, match2]):
            if match1:
                out.append(int(index))
            elif match2:
                out += list(range(int(match2.group(1)), int(match2.group(2)) + 1))
    return ", ".join([str(i) for i in sorted(list(set(out)))])


