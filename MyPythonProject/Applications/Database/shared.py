# -*- coding: ISO-8859-1 -*-
from contextlib import contextmanager
import sqlite3

__author__ = 'Xavier ROSSET'


# ========
# Classes.
# ========
class Boolean(object):

    def __init__(self, s):
        self.bool = False
        if s.upper() == "Y":
            self.bool = True


# ==========
# Functions.
# ==========
# @contextmanager
# def connectto(db):
#     conn = sqlite3.connect(db, detect_types=sqlite3.PARSE_DECLTYPES)
#     conn.row_factory = sqlite3.Row
#     yield conn
#     conn.commit()
#     conn.close()


def adapt_boolean(b):
    d = {False: 0, True: 1}
    return d[b.bool]


def convert_boolean(i):
    d = {0: False, 1: True}
    return d[int(i)]
