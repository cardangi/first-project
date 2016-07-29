# -*- coding: ISO-8859-1 -*-
from contextlib import contextmanager
import sqlite3
from ... import shared

__author__ = 'Xavier ROSSET'


@contextmanager
def toto(database):
    conn = sqlite3.connect(database, detect_types=sqlite3.PARSE_DECLTYPES)
    conn.row_factory = sqlite3.Row
    yield conn.cursor()
    conn.close()

with toto(shared.DATABASE) as c:
    for row in c.execute("SELECT * FROM lastrundates ORDER BY rowid"):
        print(row["id"])

with toto(shared.DATABASE) as c:
    for row in c.execute("SELECT * FROM backup ORDER BY rowid"):
        print(row["id"])

with toto(shared.DATABASE) as c:
    for row in c.execute("SELECT * FROM rippinglog ORDER BY rowid"):
        print(row["id"])
