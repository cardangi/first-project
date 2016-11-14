# -*- coding: ISO-8859-1 -*-
import re
import json
import sqlite3
from datetime import datetime
from ...shared import DATABASE
from ..shared import connectto, Boolean
from collections import MutableSequence

__author__ = 'Xavier ROSSET'


# ========
# Classes.
# ========
class Tracks(MutableSequence):

    def __init__(self, fil):
        self._seq = []
        self._fil = fil

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


class InsertTracks(Tracks):

    def __init__(self, fil):
        super(InsertTracks, self).__init__(fil)
        for index, albumsort, titlesort, artist, year, album, genre, discnumber, totaldiscs, label, tracknumber, totaltracks, title, live, bootleg, incollection, upc, encodingyear, titlelanguage, origyear \
                in json.load(self._fil):

            # Check if origyear is valid.
            try:
                origyear = validyear(origyear)
            except ValueError:
                continue

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

            # Check if encodingyear is valid.
            try:
                encodingyear = validyear(encodingyear)
            except ValueError:
                continue

            tupalbum = (index[:-11], artist, year, album, totaldiscs, genre, Boolean(live), Boolean(bootleg), Boolean(incollection), titlelanguage, upc, encodingyear, datetime.now(), origyear)
            tupdisc = (index[:-11], discnumber, totaltracks, datetime.now())
            tuptrack = (index[:-11], discnumber, tracknumber, title, datetime.now())
            self._seq.append([tupalbum, tupdisc, tuptrack])


class DeleteTracks(Tracks):

    def __init__(self, fil):
        super(DeleteTracks, self).__init__(fil)
        for uid in json.load(self._fil):
            try:
                uid = validid(uid)
            except ValueError:
                continue
            self._seq.append((uid,))


# ==========
# Functions.
# ==========
def insertfromfile(fil, db=DATABASE):
    statusss = []
    with connectto(db) as c:
        tracks = InsertTracks(fil)
        if len(tracks):
            for album, disc, track in tracks:
                statuss = []

                # TRACKS table.
                status = 0
                try:
                    c.execute("INSERT INTO tracks (albumid, discid, trackid, title, created) VALUES (?, ?, ?, ?, ?)", track)
                except (sqlite3.Error, ValueError):
                    status = 100
                    pass
                except sqlite3.IntegrityError:
                    status = 99
                    pass
                statuss.append(status)

                # DISCS table.
                status = 0
                try:
                    c.execute("INSERT INTO discs (albumid, discid, tracks, created) VALUES (?, ?, ?, ?)", disc)
                except (sqlite3.Error, ValueError):
                    status = 100
                    pass
                except sqlite3.IntegrityError:
                    status = 99
                    pass
                statuss.append(status)

                # ALBUMS table.
                status = 0
                try:
                    c.execute("INSERT INTO albums (albumid, artist, year, album, discs, genre, live, bootleg, incollection, language, upc, encodingyear, created, origyear) "
                              "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", album)
                except (sqlite3.Error, ValueError):
                    status = 100
                    pass
                except sqlite3.IntegrityError:
                    status = 99
                    pass
                statuss.append(status)

                statusss.append(tuple(statuss))
    return statusss


# def deletefromfile(fil, db=DATABASE):
#     status = 100
#     with connectto(db) as c:
#         tracks = DeleteTracks(fil)
#         if len(tracks):
#             try:
#                 c.executemany("DELETE FROM rippinglog WHERE id=?", tracks)
#             except (sqlite3.Error, ValueError):
#                 pass
#             else:
#                 status = 0
#     return status


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
