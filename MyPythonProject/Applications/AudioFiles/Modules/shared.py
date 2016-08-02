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
    :param indexes: string with required indexes. "1, 2, 3" or "1-10" are only allowed.
    :param files: files list.
    :return: list of corresponding files.
    """
    indexes_list = []
    rex1 = re.compile(r"^(\d\d?,\s)*(\d\d?)$")
    rex2 = re.compile(r"^(\d{1,2})\-(\d{1,2})$")
    match1 = rex1.match(indexes)
    match2 = rex2.match(indexes)
    if all([not match1, not match2]):
        return []
    if match1:
        indexes_list = indexes.split(", ")
    elif match2:
        indexes_list = list(range(int(match2.group(1)), int(match2.group(2)) + 1))
    return [files[int(i) - 1] for i in indexes_list if int(i) <= len(files)]
