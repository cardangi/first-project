# -*- coding: utf-8 -*-
import os
import re
import sys
import yaml
import logging
import argparse
from logging.config import dictConfig
from collections import MutableMapping
from Applications.Database.AudioCD.shared import update

__author__ = 'Xavier ROSSET'


# ========
# Classes.
# ========
class UpdateRippingLog(MutableMapping):

    inputs = {"1": ("Enter record(s) unique ID", "uid"),
              "2": ("Enter artist new value ", "artist"),
              "3": ("Enter year new value", "year"),
              "4": ("Enter album new value", "album"),
              "5": ("Enter UPC new value", "upc"),
              "6": ("Enter genre new value", "genre"),
              "7": ("Enter albumsort new value", "albumsort"),
              "8": ("Enter artistsort new value", "artistsort")}

    def __init__(self):
        self._upc = None
        self._year = None
        self._album = None
        self._genre = None
        self._artist = None
        self._albumsort = None
        self._artistsort = None
        self._index, self._uid, self._query = 0, [], {}

    def __call__(self, *args, **kwargs):
        self._index += 1
        return self.inputs[str(self._index)]

    def __getitem__(self, item):
        return self._query[item]

    def __setitem__(self, key, value):
        self._query[key] = value

    def __delitem__(self, key):
        del self._query[key]

    def __iter__(self):
        return iter(self._query)

    def __len__(self):
        return len(self._query)

    # ------
    # INDEX.
    # ------
    @property
    def index(self):
        return self._index

    # -------------
    # RECORD(S) ID.
    # -------------
    @property
    def uid(self):
        return list(self._uid)

    @uid.setter
    def uid(self, arg):
        self._uid = arg

    # -------
    # ARTIST.
    # -------
    @property
    def artist(self):
        return self._artist

    @artist.setter
    def artist(self, arg):
        self._artist = arg
        self._query["artist"] = arg

    # -----
    # YEAR.
    # -----
    @property
    def year(self):
        return self._year

    @year.setter
    def year(self, arg):
        self._year = arg
        self._query["year"] = arg

    # ------
    # ALBUM.
    # ------
    @property
    def album(self):
        return self._album

    @album.setter
    def album(self, arg):
        self._album = arg
        self._query["album"] = arg

    # ----
    # UPC.
    # ----
    @property
    def upc(self):
        return self._upc

    @upc.setter
    def upc(self, arg):
        self._upc = arg
        self._query["upc"] = arg

    # ------
    # GENRE.
    # ------
    @property
    def genre(self):
        return self._genre

    @genre.setter
    def genre(self, arg):
        self._genre = arg
        self._query["genre"] = arg

    # ----------
    # ALBUMSORT.
    # ----------
    @property
    def albumsort(self):
        return self._albumsort

    @albumsort.setter
    def albumsort(self, arg):
        self._albumsort = arg
        self._query["albumsort"] = arg

    # -----------
    # ARTISTSORT.
    # -----------
    @property
    def artistsort(self):
        return self._artistsort

    @artistsort.setter
    def artistsort(self, arg):
        self._artistsort = arg
        self._query["artistsort"] = arg


# ==========
# Functions.
# ==========
def validdb(arg):
    if not os.path.exists(arg):
        raise argparse.ArgumentTypeError('"{0}" doesn\'t exist.'.format(arg))
    return arg


# =================
# Arguments parser.
# =================
parser = argparse.ArgumentParser()
parser.add_argument("-d", "--db", dest="database", default=os.path.join(os.path.expandvars("%_COMPUTING%"), "database.db"), type=validdb)


# ================
# Initializations.
# ================
regex, arguments = re.compile("\d(?:\d(?:\d(?:\d)?)?)?"), parser.parse_args()


# ===============
# Main algorithm.
# ===============
if __name__ == "__main__":

    with open(os.path.join(os.path.expandvars("%_COMPUTING%"), "logging.yml"), encoding="UTF_8") as fp:
        dictConfig(yaml.load(fp))
    logger = logging.getLogger("Default.{0}".format(os.path.splitext(os.path.basename(__file__))[0]))

    choice, records = None, UpdateRippingLog()
    while True:
        try:
            inp, fld = records()
            while True:
                choice = input("{0}. {1}: ".format(records.index, inp))
                if records.index == 1:
                    uid = regex.findall(choice)
                    if uid:
                        choice = uid
                        break
                    continue
                break
            if choice:
                setattr(records, fld, choice)
        except KeyError:
            break

    logger.debug(records.uid)
    for tup in records.items():
        logger.debug("{t[0]}: {t[1]}".format(t=tup))
    sys.exit(update(*records.uid, db=arguments.database, **records))