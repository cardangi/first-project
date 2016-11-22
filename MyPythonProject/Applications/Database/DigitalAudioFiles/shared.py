# -*- coding: ISO-8859-1 -*-
import re
import json
import sqlite3
import logging
from datetime import datetime
from ...shared import DATABASE
from collections import MutableSequence
from ..shared import Boolean, adapt_boolean, convert_boolean

__author__ = 'Xavier ROSSET'


# ================
# SQLite3 adapter.
# ================
sqlite3.register_adapter(Boolean, adapt_boolean)


# ==================
# SQLite3 converter.
# ==================
sqlite3.register_converter("boolean", convert_boolean)


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


# ===================================
# Main functions to work with tables.
# ===================================
def insertfromfile(fil, db=DATABASE):
    statusss = []
    tracks = InsertTracksfromFile(fil)
    logger = logging.getLogger("{0}.insertfromfile".format(__name__))
    if len(tracks):
        for album, disc, track in tracks:
            statuss, acount, dcount, tcount = [], 0, 0, 0

            conn = sqlite3.connect(db)
            try:
                with conn:

                    # TRACKS table.
                    try:
                        conn.execute("INSERT INTO tracks (albumid, discid, trackid, title, created) VALUES (?, ?, ?, ?, ?)", track)
                        tcount = conn.total_changes
                        logger.debug("TRACKS: {0} records inserted.".format(tcount))
                    except sqlite3.IntegrityError:
                        pass

                    # DISCS table.
                    try:
                        conn.execute("INSERT INTO discs (albumid, discid, tracks, created) VALUES (?, ?, ?, ?)", disc)
                        dcount = conn.total_changes - tcount
                        logger.debug("DISCS: {0} records inserted.".format(dcount))
                    except sqlite3.IntegrityError:
                        pass

                    # ALBUMS table.
                    try:
                        conn.execute("INSERT INTO albums (albumid, artist, year, album, discs, genre, live, bootleg, incollection, language, upc, encodingyear, created, origyear) "
                                     "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", album)
                        acount = conn.total_changes - tcount - dcount
                        logger.debug("ALBUMS: {0} records inserted.".format(acount))
                    except sqlite3.IntegrityError:
                        pass

                    statuss = [tcount, dcount, acount]

            except sqlite3.Error:
                statuss = [0, 0, 0]

            statusss.append(tuple(statuss))
    return statusss


def select(db=DATABASE):
    conn = sqlite3.connect(db, detect_types=sqlite3.PARSE_DECLTYPES)
    conn.row_factory = sqlite3.Row
    for arow in conn.execute("SELECT a.rowid, a.albumid, artist, year, album, discs, genre, live, bootleg, incollection, language, upc, encodingyear, a.created, origyear, b.discid, b.tracks, trackid, title "
                             "FROM albums a "
                             "JOIN discs b ON a.albumid=b.albumid "
                             "JOIN tracks c ON a.albumid=c.albumid AND b.discid=c.discid "
                             "ORDER BY a.albumid, b.discid, c.trackid"):
            yield tuple(arow)


def select2(db=DATABASE):
    conn = sqlite3.connect(db, detect_types=sqlite3.PARSE_DECLTYPES)
    conn.row_factory = sqlite3.Row
    for arow in conn.execute("SELECT a.rowid, a.albumid, artist, year, album, discs, genre, live, bootleg, incollection, language, upc, encodingyear, a.created, origyear, b.discid, b.tracks, trackid, title "
                             "FROM albums a "
                             "JOIN discs b ON a.albumid=b.albumid "
                             "JOIN tracks c ON a.albumid=c.albumid AND b.discid=c.discid "
                             "ORDER BY a.created DESC, a.albumid, b.discid, c.trackid"):
            yield tuple(arow)


def selectfromuid(uid, db=DATABASE):
    conn = sqlite3.connect(db, detect_types=sqlite3.PARSE_DECLTYPES)
    conn.row_factory = sqlite3.Row
    for arow in conn.execute("SELECT a.rowid, a.albumid, artist, year, album, discs, genre, live, bootleg, incollection, language, upc, encodingyear, a.created, origyear, b.discid, b.tracks, trackid, title "
                             "FROM albums a "
                             "JOIN discs b ON a.albumid=b.albumid "
                             "JOIN tracks c ON a.albumid=c.albumid AND b.discid=c.discid "
                             "WHERE a.rowid=? "
                             "ORDER BY a.albumid, b.discid, c.trackid", (uid,)):
            yield tuple(arow)


def deletefromuid(uid, db=DATABASE):

    acount, dcount, tcount, discs, tracks, conn = 0, 0, 0, [], [], sqlite3.connect(db)
    conn.row_factory = sqlite3.Row

    for arow in conn.execute("SELECT albumid FROM albums WHERE rowid=?", (uid,)):
        for drow in conn.execute("SELECT rowid, discid FROM discs WHERE albumid=?", (arow["albumid"],)):
            discs.append(drow["rowid"])
            for trow in conn.execute("SELECT rowid FROM tracks WHERE albumid=? AND discid=?", (arow["albumid"], drow["discid"])):
                tracks.append(trow["rowid"])

    try:
        with conn:

            # TRACKS table.
            conn.executemany("DELETE FROM tracks WHERE rowid=?", [(i,) for i in tracks])
            tcount = conn.total_changes

            # DISCS table.
            conn.executemany("DELETE FROM discs WHERE rowid=?", [(i,) for i in discs])
            dcount = conn.total_changes - tcount

            # ALBUMS table.
            conn.execute("DELETE FROM albums WHERE rowid=?", (uid,))
            acount = conn.total_changes - tcount - dcount

    except (sqlite3.Error, ValueError):
        return 0, 0, 0

    return acount, dcount, tcount


def deletealbumsfromuid(*uid, db=DATABASE):

    status, conn = 0, sqlite3.connect(db)
    with conn:
        conn.executemany("DELETE FROM albums WHERE rowid=?", [(i,) for i in uid])
        status = conn.total_changes
    return status


def deletediscsfromuid(*uid, db=DATABASE):

    status, conn = 0, sqlite3.connect(db)
    with conn:
        conn.executemany("DELETE FROM discs WHERE rowid=?", [(i,) for i in uid])
        status = conn.total_changes
    return status


def deletetracksfromuid(*uid, db=DATABASE):

    status, conn = 0, sqlite3.connect(db)
    with conn:
        conn.executemany("DELETE FROM tracks WHERE rowid=?", [(i,) for i in uid])
        status = conn.total_changes
    return status
