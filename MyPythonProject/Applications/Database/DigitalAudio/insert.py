# -*- coding: ISO-8859-1 -*-
__author__ = 'Xavier ROSSET'


# =================
# Absolute imports.
# =================
from datetime import datetime
import argparse
import sqlite3
import locale
import csv


# =================
# Relative imports.
# =================
from ... import shared


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
class Boolean:
    def __init__(self, b):
        self.bool = b


# ==========
# Functions.
# ==========
def adapt_boolean(o):
    if o.bool:
        return 1
    return 0
sqlite3.register_adapter(Boolean, adapt_boolean)


def convert_boolean(f):
    if int(f):
        return True
    return False
sqlite3.register_converter("boolean", convert_boolean)


def convertstringtoboolean(s):
    if s == "Y":
        return True
    return False


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


# ===============
# Main algorithm.
# ===============

# 1. Ouverture de la connexion à la base de données.
conn = sqlite3.connect(shared.DATABASE, detect_types=sqlite3.PARSE_DECLTYPES)
conn.row_factory = sqlite3.Row

# 2. Traitement de la requête.
reader = csv.DictReader(arguments.fromfile, delimiter=";", fieldnames=HEADERS)
for row in reader:

    # ALBUMS table.
    tupalbum = (row["index"][:-11], row["artist"], int(row["year"]), row["album"], int(row["totaldiscs"]), row["genre"], Boolean(convertstringtoboolean(row["live"])), Boolean(convertstringtoboolean(row["bootleg"])),
                Boolean(convertstringtoboolean(row["incollection"])), row["language"], row["upc"], convertyeartointeger(row["encodingyear"]), datetime.now(), convertyeartointeger(row["origyear"]))
    try:
        conn.cursor().execute("INSERT INTO albums (albumid, artist, year, album, discs, genre, live, bootleg, incollection, language, upc, encodingyear, created, origyear)"
                              " VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", tupalbum)
    except sqlite3.IntegrityError:
        pass

    # DISCS table.
    tupdisc = (row["index"][:-11], int(row["discnumber"]), int(row["totaltracks"]), datetime.now())
    try:
        conn.cursor().execute("INSERT INTO discs (albumid, discid, tracks, created) VALUES (?, ?, ?, ?)", tupdisc)
    except sqlite3.IntegrityError:
        pass

    # TRACKS table.
    tuptrack = (row["index"][:-11], int(row["discnumber"]), int(row["track"]), row["title"], datetime.now())
    try:
        conn.cursor().execute("INSERT INTO tracks (albumid, discid, trackid, title, created) VALUES (?, ?, ?, ?, ?)", tuptrack)
    except sqlite3.IntegrityError:
        pass

# 3. Mise à jour de la base de données.
conn.commit()

# 4. Fermeture de la connexion à la base de données.
conn.close()
