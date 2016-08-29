# -*- coding: ISO-8859-1 -*-
from contextlib import contextmanager
from datetime import datetime
import argparse
import sqlite3
import locale
import csv
from ... import shared

__author__ = 'Xavier ROSSET'


# ==========================
# Define French environment.
# ==========================
locale.setlocale(locale.LC_ALL, "")


# =================
# Arguments parser.
# =================
parser = argparse.ArgumentParser()
parser.add_argument("fromfile", type=argparse.FileType(encoding=shared.DFTENCODING))


# ========
# Classes.
# ========
class Boolean(object):

    def __init__(self, s):
        self.bool = False
        if s.upper() == "Y":
            self.bool = True

    def __repr__(self):
        return "{0}".format(self.bool).lower()


# ==========
# Functions.
# ==========
@contextmanager
def connectto(db):
    conn = sqlite3.connect(db, detect_types=sqlite3.PARSE_DECLTYPES)
    conn.row_factory = sqlite3.Row
    yield conn.cursor()
    conn.commit()
    conn.close()


def adapt_boolean(b):
    d = {False: 0, True: 1}
    return d[b.bool]


def convert_boolean(i):
    d = {0: False, 1: True}
    return d[int(i)]


def convertyeartointeger(s):
    import re
    regex = re.compile(r"^(?:19[6-9][0-9]|20(?:[0-9]){2})$")
    match = regex.search(s)
    if match:
        return int(s)
    return 0


# ==========
# Constants.
# ==========
HEADERS = ["index", "albumsort", "titlesort", "artist", "year", "album", "genre", "discnumber", "totaldiscs", "publisher", "track", "totaltracks", "title", "live", "bootleg", "incollection", "upc", "encodingyear",
           "language", "origyear"]


# ================
# Initializations.
# ================
arguments = parser.parse_args()
sqlite3.register_adapter(Boolean, adapt_boolean)
sqlite3.register_converter("boolean", convert_boolean)


# ===============
# Main algorithm.
# ===============
with connectto(shared.DATABASE) as c:

    reader = csv.DictReader(arguments.fromfile, delimiter=";", fieldnames=HEADERS)
    for row in reader:

        # ALBUMS table.
        tupalbum = (row["index"][:-11], row["artist"], int(row["year"]), row["album"], int(row["totaldiscs"]), row["genre"], Boolean(row["live"]), Boolean(row["bootleg"]), Boolean(row["incollection"]),
                    row["language"], row["upc"], convertyeartointeger(row["encodingyear"]), datetime.now(), convertyeartointeger(row["origyear"]))
        try:
            c.execute("INSERT INTO albums (albumid, artist, year, album, discs, genre, live, bootleg, incollection, language, upc, encodingyear, created, origyear) "
                      "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", tupalbum)
        except sqlite3.IntegrityError:
            pass

        # DISCS table.
        tupdisc = (row["index"][:-11], int(row["discnumber"]), int(row["totaltracks"]), datetime.now())
        try:
            c.execute("INSERT INTO discs (albumid, discid, tracks, created) VALUES (?, ?, ?, ?)", tupdisc)
        except sqlite3.IntegrityError:
            pass

        # TRACKS table.
        tuptrack = (row["index"][:-11], int(row["discnumber"]), int(row["track"]), row["title"], datetime.now())
        try:
            c.execute("INSERT INTO tracks (albumid, discid, trackid, title, created) VALUES (?, ?, ?, ?, ?)", tuptrack)
        except sqlite3.IntegrityError:
            pass
