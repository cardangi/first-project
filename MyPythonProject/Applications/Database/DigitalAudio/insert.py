# -*- coding: ISO-8859-1 -*-
from datetime import datetime
import argparse
import sqlite3
import locale
import json
import os
from ... import shared as s1
from ..Modules import shared as s2

__author__ = 'Xavier ROSSET'


# ==========================
# Define French environment.
# ==========================
locale.setlocale(locale.LC_ALL, "")


# ==========
# Functions.
# ==========
def convertyeartointeger(s):
    import re
    regex = re.compile(r"^(?:19[6-9][0-9]|20(?:[0-9]){2})$")
    match = regex.search(s)
    if match:
        return int(s)
    return 0


def validfile(s):
    if not os.path.exists(s):
        raise argparse.ArgumentTypeError('"{0}" doesn\'t exist.'.format(s))
    return s


# =================
# Arguments parser.
# =================
parser = argparse.ArgumentParser()
parser.add_argument("fromjsonfile", type=validfile)


# ================
# Initializations.
# ================
arguments = parser.parse_args()


# ===============
# SQLite adapter.
# ===============
sqlite3.register_adapter(s2.Boolean, s2.adapt_boolean)


# ===============
# Main algorithm.
# ===============
with s2.connectto(s1.DATABASE) as c:

    with open(arguments.fromjsonfile) as fp:
        for index, \
            albumsort, \
            titlesort, \
            artist, \
            year, \
            album, \
            genre, \
            discnumber, \
            totaldiscs, \
            label, \
            tracknumber, \
            totaltracks, \
            title, \
            live, \
            bootleg, \
            incollection, \
            upc, \
            encodingyear, \
            titlelanguage, \
            origyear \
                in json.load(fp):

            # ALBUMS table.
            tupalbum = (index[:-11], artist, int(year), album, int(totaldiscs), genre, s2.Boolean(live), s2.Boolean(bootleg), s2.Boolean(incollection), titlelanguage, upc, convertyeartointeger(encodingyear),
                        datetime.now(), convertyeartointeger(origyear))
            try:
                c.execute("INSERT INTO albums (albumid, artist, year, album, discs, genre, live, bootleg, incollection, language, upc, encodingyear, created, origyear) "
                          "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", tupalbum)
            except sqlite3.IntegrityError:
                pass
    
            # DISCS table.
            tupdisc = (index[:-11], int(discnumber), int(totaltracks), datetime.now())
            try:
                c.execute("INSERT INTO discs (albumid, discid, tracks, created) VALUES (?, ?, ?, ?)", tupdisc)
            except sqlite3.IntegrityError:
                pass
    
            # TRACKS table.
            tuptrack = (index[:-11], int(discnumber), int(tracknumber), title, datetime.now())
            try:
                c.execute("INSERT INTO tracks (albumid, discid, trackid, title, created) VALUES (?, ?, ?, ?, ?)", tuptrack)
            except sqlite3.IntegrityError:
                pass
