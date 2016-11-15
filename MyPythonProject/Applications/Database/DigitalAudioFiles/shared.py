# -*- coding: ISO-8859-1 -*-
import re
import json
import sqlite3
from datetime import datetime
from ...shared import DATABASE
from collections import MutableSequence
from ..shared import Boolean, adapt_boolean


__author__ = 'Xavier ROSSET'


# ================
# SQLite3 adapter.
# ================
sqlite3.register_adapter(Boolean, adapt_boolean)


# ========
# Classes.
# ========
class InsertTracksfromFile(MutableSequence):

    def __init__(self, fil):
        self._seq = []
        for index, albumsort, titlesort, artist, year, album, genre, discnumber, totaldiscs, label, tracknumber, totaltracks, title, live, bootleg, incollection, upc, encodingyear, titlelanguage, \
            origyear in json.load(fil):

            # Check if year is valid.
            try:
                year = validyear(year)
            except ValueError:
                continue

            # Check if discnumber is valid.
            try:
                discnumber = int(discnumber)
            except ValueError:
                continue

            # Check if totaldiscs is valid.
            try:
                totaldiscs = int(totaldiscs)
            except ValueError:
                continue

            # Check if tracknumber is valid.
            try:
                tracknumber = int(tracknumber)
            except ValueError:
                continue

            # Check if totaltracks is valid.
            try:
                totaltracks = int(totaltracks)
            except ValueError:
                continue

            # Check if product code is valid.
            try:
                upc = validbarcode(upc)
            except ValueError:
                continue

            # Check if genre is valid.
            try:
                genre = validgenre(genre)
            except ValueError:
                continue

            # Set origyear.
            try:
                origyear = validyear(origyear)
            except ValueError:
                origyear = 0

            # Set encodingyear.
            try:
                encodingyear = validyear(encodingyear)
            except ValueError:
                encodingyear = 0

            tupalbum = (index[:-11], artist, year, album, totaldiscs, genre, Boolean(live), Boolean(bootleg), Boolean(incollection), titlelanguage, upc, encodingyear, datetime.now(), origyear)
            tupdisc = (index[:-11], discnumber, totaltracks, datetime.now())
            tuptrack = (index[:-11], discnumber, tracknumber, title, datetime.now())
            self._seq.append([tupalbum, tupdisc, tuptrack])

    def __getitem__(self, item):
        return self._seq[item]

    def __setitem__(self, key, value):
        self._seq[key] = value

    def __delitem__(self, key):
        del self._seq[key]

    def __len__(self):
        return len(self._seq)

    def insert(self, index, value):
        self._seq.insert(index, value)


# ==========
# Functions.
# ==========
def validyear(s):
    regex = re.compile(r"^(19[6-9]|20[0-2])\d$")
    if not regex.match(s):
        raise ValueError('"{0}" is not a valid year'.format(s))
    return int(s)


def validbarcode(s):
    regex = re.compile("^\d{12,13}$")
    if s:
        if not regex.match(s):
            raise ValueError('"{0}" is not a valid barcode'.format(s))
    return s


def validgenre(s):
    if s not in ["Rock", "Hard Rock", "Heavy Metal", "Trash Metal", "Alternative Rock", "Black Metal", "Progressive Rock"]:
        raise ValueError('"{0}" is not a valid genre'.format(s))
    return s


def validid(s):
    regex = re.compile("^\d(?:\d(?:\d)?)?$")
    s = str(s)
    if not regex.match(s):
        raise ValueError('"{0}" is not a valid ID'.format(s))
    return int(s)


def insertfromfile(fil, db=DATABASE):
    statusss = []
    tracks = InsertTracksfromFile(fil)
    if len(tracks):
        for album, disc, track in tracks:
            statuss, acount, dcount, tcount = [], 0, 0, 0

            conn = sqlite3.connect(db, detect_types=sqlite3.PARSE_DECLTYPES)
            try:
                with conn:

                    # TRACKS table.
                    try:
                        conn.execute("INSERT INTO tracks (albumid, discid, trackid, title, created) VALUES (?, ?, ?, ?, ?)", track)
                        tcount = conn.total_changes
                    except sqlite3.IntegrityError:
                        pass

                    # DISCS table.
                    try:
                        conn.execute("INSERT INTO discs (albumid, discid, tracks, created) VALUES (?, ?, ?, ?)", disc)
                        dcount = conn.total_changes - tcount
                    except sqlite3.IntegrityError:
                        pass

                    # ALBUMS table.
                    try:
                        conn.execute("INSERT INTO albums (albumid, artist, year, album, discs, genre, live, bootleg, incollection, language, upc, encodingyear, created, origyear) "
                                     "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", album)
                        acount = conn.total_changes - tcount - dcount
                    except sqlite3.IntegrityError:
                        pass

                    statuss = [tcount, dcount, acount]

            except sqlite3.Error:
                statuss = [0, 0, 0]

            statusss.append(tuple(statuss))
    return statusss


def selectfromuid(uid, db=DATABASE):

    conn = sqlite3.connect(db, detect_types=sqlite3.PARSE_DECLTYPES)
    conn.row_factory = sqlite3.Row
    album, discs, tracks = None, [], []

    for arow in conn.execute("SELECT albumid, artist, year, album, discs, genre, live, bootleg, incollection, language, upc, encodingyear, created, origyear FROM albums WHERE rowid=?", (uid,)):
        album = tuple(arow)
        for drow in conn.execute("SELECT albumid, discid, tracks, created FROM discs WHERE albumid=?", (arow["albumid"],)):
            discs.append(tuple(drow))
            for trow in conn.execute("SELECT albumid, discid, trackid, title, created FROM tracks WHERE albumid=? AND discid=?", (arow["albumid"], drow["discid"])):
                tracks.append(tuple(trow))

    return album, discs, tracks


def deletefromuid(uid, db=DATABASE):

    status, acount, dcount, tcount, r1, r2, r3, conn = (0, 0, 0), 0, 0, 0, (), [], [], sqlite3.connect(db)
    conn.row_factory = sqlite3.Row
    for arow in conn.execute("SELECT albumid FROM albums WHERE rowid=?", (uid,)):
        r1 = (uid,)
        for drow in conn.execute("SELECT rowid, discid FROM discs WHERE albumid=?", (arow["albumid"],)):
            r2.append(drow["rowid"])
            for trow in conn.execute("SELECT rowid FROM tracks WHERE albumid=? AND discid=?", (arow["albumid"], drow["discid"])):
                r3.append(trow["rowid"])

    if any([r1, r2, r3]):
        try:
            with conn:
                conn.executemany("DELETE FROM albums WHERE rowid=?", [(i,) for i in r1])
                acount = conn.total_changes
                conn.executemany("DELETE FROM discs WHERE rowid=?", [(i,) for i in tuple(r2)])
                dcount = conn.total_changes - acount
                conn.executemany("DELETE FROM tracks WHERE rowid=?", [(i,) for i in tuple(r3)])
                tcount = conn.total_changes - acount - dcount
        except sqlite3.Error:
            pass
    return acount, dcount, tcount


def deletealbumsfromuid(*uid, db=DATABASE):

    status, conn = 0, sqlite3.connect(db)
    try:
        with conn:
            conn.executemany("DELETE FROM albums WHERE rowid=?", [(i,) for i in list(uid)])
            status = conn.total_changes
    except (sqlite3.Error, ValueError):
        pass
    return status


def deletediscsfromuid(*uid, db=DATABASE):

    status, conn = 0, sqlite3.connect(db)
    try:
        with conn:
            conn.executemany("DELETE FROM discs WHERE rowid=?", [(i,) for i in list(uid)])
            status = conn.total_changes
    except (sqlite3.Error, ValueError):
        pass
    return status


def deletetracksfromuid(*uid, db=DATABASE):

    status, conn = 0, sqlite3.connect(db)
    try:
        with conn:
            conn.executemany("DELETE FROM tracks WHERE rowid=?", [(i,) for i in list(uid)])
            status = conn.total_changes
    except (sqlite3.Error, ValueError):
        pass
    return status
