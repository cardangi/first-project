# -*- coding: utf-8 -*-
import os
import re
import sys
import yaml
import logging
from Applications import shared
from logging.config import dictConfig
from collections import MutableMapping
from Applications.Database.AudioCD.shared import update

__author__ = 'Xavier ROSSET'


# ========
# Classes.
# ========
class RippingLog(MutableMapping):

    inputs = {"1": ("Enter record(s) unique ID", "uid"),
              "2": ("Enter artist new value ", "artist"),
              "3": ("Enter year new value", "year"),
              "4": ("Enter album new value", "album"),
              "5": ("Enter UPC new value", "upc"),
              "6": ("Enter genre new value", "genre"),
              "7": ("Enter albumsort new value", "albumsort"),
              "8": ("Enter artistsort new value", "artistsort"),
              "9": ("Enter database to update", "database")}

    def __init__(self):
        self._upc = None
        self._year = None
        self._album = None
        self._genre = None
        self._artist = None
        self._albumsort = None
        self._artistsort = None
        self._index, self._step, self._uid, self._query = None, 0, [], {}

    def __call__(self, *args, **kwargs):
        self._step += 1
        return self.inputs[str(self.index)]

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

    @index.setter
    def index(self, arg):
        self._index = arg

    # -----
    # STEP.
    # -----
    @property
    def step(self):
        return self._step

    # -------------
    # RECORD(S) ID.
    # -------------
    @property
    def uid(self):
        return self._uid

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


# ================
# Initializations.
# ================
database, rex1, rex2, rex3 = None, \
                             re.compile("\d(?:\d(?:\d(?:\d)?)?)?"), \
                             re.compile(r"^(?:{0})$".format(shared.DFTYEARREGEX)), \
                             re.compile(r"^1\.(?:{0})0000\.\d$".format(shared.DFTYEARREGEX)), \


# ===============
# Main algorithm.
# ===============
if __name__ == "__main__":

    with open(os.path.join(os.path.expandvars("%_COMPUTING%"), "logging.yml"), encoding="UTF_8") as fp:
        dictConfig(yaml.load(fp))
    logger = logging.getLogger("Default.{0}".format(os.path.splitext(os.path.basename(__file__))[0]))

    choice, record = None, RippingLog()
    record.index = 0
    while True:
        try:
            record.index += 1
            inp, fld = record()
            while True:
                choice = input("{0}. {1}: ".format(record.step, inp))

                # Check if record(s) ID are coherent.
                if fld == "uid":
                    uid = rex1.findall(choice)
                    if uid:
                        choice = uid
                        break
                    continue

                # Check if year is coherent.
                elif fld == "year":
                    if rex2.match(choice):
                        choice = int(choice)
                        break
                    continue

                # Check if albumsort is coherent.
                elif fld == "albumsort":
                    if rex3.match(choice):
                        break
                    continue

                # Check chosen database.
                elif fld == "database":
                    if choice:
                        choice = choice.replace('"', '')
                    if choice and os.path.exists(choice) and os.path.isfile(choice):
                        database = choice
                        break
                    database = shared.DATABASE
                    break

                break
            if choice:
                setattr(record, fld, choice)

        except KeyError:
            break

    logger.debug(database)
    logger.debug(record.uid)
    for tup in record.items():
        logger.debug("{t[0]}: {t[1]}".format(t=tup))
        logger.debug(type(tup[1]))
    sys.exit(update(*record.uid, db=database, **record))
