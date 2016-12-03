# -*- coding: ISO-8859-1 -*-
import re
import json
import sqlite3
import logging
from itertools import repeat
from datetime import datetime
from ...shared import DATABASE
from collections import MutableSequence

__author__ = 'Xavier ROSSET'


# ========
# Classes.
# ========
class InsertTracksfromFile(MutableSequence):

    def __init__(self, fil):
        self._seq = []
        for artist, year, album, genre, productcode, albumsort, artistsort in json.load(fil):

            # Check if year is valid.
            try:
                year = validyear(year)
            except ValueError:
                continue

            # Check if genre is valid.
            try:
                genre = validgenre(genre)
            except ValueError:
                continue

            # Check if productcode is valid.
            try:
                productcode = validproductcode(productcode)
            except ValueError:
                continue

            # Check if albumsort is valid.
            try:
                albumsort = validalbumsort(albumsort)
            except ValueError:
                continue

            self._seq.append((datetime.now(), artist, year, album, productcode, genre, "dBpoweramp 15.1", albumsort, artistsort))

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


def validgenre(s):
    if s not in ["Rock", "Hard Rock", "Heavy Metal", "Trash Metal", "Alternative Rock", "Black Metal", "Progressive Rock"]:
        raise ValueError('"{0}" is not a valid genre'.format(s))
    return s


def validalbumsort(s):
    regex = re.compile("^(?=[\d.]+$)(?=.\.[^.]+\..$)(?=\d\.\d{8}\.\d$).\.(?:19[6-9]|20[01])\d{5}\..$")
    if not regex.match(s):
        raise ValueError('"{0}" is not a valid albumsort'.format(s))
    return s


def validproductcode(s):
    regex = re.compile("^\d{12,13}$")
    if s:
        if not regex.match(s):
            raise ValueError('"{0}" is not a valid productcode'.format(s))
    return s


# ===================================
# Main functions to work with tables.
# ===================================
def insertfromfile(fil, db=DATABASE):
    status, tracks = 0, InsertTracksfromFile(fil)
    if len(tracks):
        conn = sqlite3.connect(db)
        with conn:
            conn.executemany("INSERT INTO rippinglog (ripped, artist, year, album, UPC, genre, application, albumsort, artistsort) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?)", tracks)
            status = conn.total_changes
            logger = logging.getLogger("{0}.insertfromfile".format(__name__))
            logger.debug("{0} records inserted.".format(status))
            if status:
                for item in tracks:  # "item" est un tuple.
                    logger.debug(item)
    return status


def deletefromuid(*uid, db=DATABASE):
    status, conn = 0, sqlite3.connect(db)
    with conn:
        conn.executemany("DELETE FROM rippinglog WHERE id=?", [(i,) for i in uid])
        status = conn.total_changes
        logger = logging.getLogger("{0}.deletefromuid".format(__name__))
        logger.debug("{0} records removed.".format(status))
        if status:
            for item in uid:
                logger.debug("Unique ID: {0:>4d}.".format(item))
    return status


def select(db=DATABASE):
    conn = sqlite3.connect(db, detect_types=sqlite3.PARSE_DECLTYPES)
    conn.row_factory = sqlite3.Row
    for row in conn.execute("SELECT * FROM rippinglog ORDER BY ripped, artistsort, albumsort"):
        logger = logging.getLogger("{0}.select".format(__name__))
        logger.debug("Selected record:")
        for item in tuple(row):
            logger.debug("\t{0}".format(item).expandtabs(3))
        yield tuple(row)


def selectfromuid(uid, db=DATABASE):
    conn = sqlite3.connect(db, detect_types=sqlite3.PARSE_DECLTYPES)
    conn.row_factory = sqlite3.Row
    for row in conn.execute("SELECT * FROM rippinglog WHERE rowid=?", (uid,)):
        logger = logging.getLogger("{0}.selectfromuid".format(__name__))
        logger.debug("Selected record:")
        logger.debug("Unique ID: {0:>4d}.".format(uid))
        for item in tuple(row):
            logger.debug("\t{0}".format(item).expandtabs(3))
        yield tuple(row)


def update(*uid, db=DATABASE, **kwargs):

    def thatfunc(a, b):
        """
        Append record unique ID b in list a.
        :param a: list.
        :param b: record unique ID.
        :return: tupled list a.
        """
        a.append(b)
        return tuple(a)

    logger = logging.getLogger("{0}.update".format(__name__))
    status, query, args = 0, "", []
    for k, v in kwargs.items():
        query = "{0}{1}=?, ".format(query, k)  # album=?, albumid=?, "
        args.append(v)  # ["the album", "T.Toto.1.19840000.1.D1.T01.NNN"]
    conn = sqlite3.connect(db)
    try:
        with conn:
            conn.executemany("UPDATE rippinglog SET {0} WHERE rowid=?".format(query[:-2]), list(map(thatfunc, repeat(args), uid)))
            # [("the album", "T.Toto.1.19840000.1.D1.T01.NNN", 1), ("the album", "T.Toto.1.19840000.1.D1.T01.NNN", 2), ("the album", "T.Toto.1.19840000.1.D1.T01.NNN", 3)]
            status = conn.total_changes
    except (sqlite3.OperationalError, sqlite3.Error) as err:
        logger.exception(err)
    else:
        logger.debug("{0:>3d} record(s) updated.".format(status))
    return status
