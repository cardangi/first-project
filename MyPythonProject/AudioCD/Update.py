# -*- coding: utf-8 -*-
import os
import re
import sys
import yaml
import logging
from Applications import shared
from logging.config import dictConfig
from Applications.Database.AudioCD.shared import update

__author__ = 'Xavier ROSSET'


# ========
# Classes.
# ========
class Interface(object):

    _regex1 = re.compile(r"\d+")
    _regex2 = re.compile(r"^(?:{0})$".format(shared.DFTYEARREGEX))
    _regex3 = re.compile(r"^1\.(?:{0})0000\.\d$".format(shared.DFTYEARREGEX))
    _regex4 = re.compile(r"\d{12,13}")
    _inputs = [("Please enter database to update", "database"),
               ("Please enter record(s) unique ID", "uid"),
               ("Please enter artist new value ", "artist"),
               ("Please enter year new value", "year"),
               ("Please enter album new value", "album"),
               ("Please enter UPC new value", "upc"),
               ("Please enter genre new value", "genre"),
               ("Please enter albumsort new value", "albumsort"),
               ("Please enter artistsort new value", "artistsort")]

    def __init__(self):
        self._upc = None
        self._year = None
        self._album = None
        self._genre = None
        self._artist = None
        self._albumsort = None
        self._artistsort = None
        self._index, self._step, self._uid, self._arguments = None, 0, [], {}

    def __iter__(self):
        return self

    def __next__(self):
        if self._index >= len(self._inputs):
            raise StopIteration
        if self._uid:
            raise StopIteration
        self._index += 1
        self._step += 1
        return self._inputs[self._index - 1]

    # -----
    # STEP.
    # -----
    @property
    def step(self):
        return self._step

    # ---------
    # DATABASE.
    # ---------
    @property
    def database(self):
        return self._database

    @database.setter
    def database(self, arg):
        val = DATABASE
        if arg:
            arg = arg.replace('"', '')
        if arg and not(os.path.exists(arg) and os.path.isfile(arg)):
            raise ValueError('"{0}" isn\'t a valid database.'.format(arg))
        elif arg and os.path.exists(arg) and os.path.isfile(arg):
            val = arg
        self._database = val

    # ----------
    # ARGUMENTS.
    # ----------
    @property
    def arguments(self):
        return self._arguments

    # ----
    # UID.
    # ----
    @property
    def uid(self):
        return self._uid

    @uid.setter
    def uid(self, arg):
        if not arg:
            raise ValueError('Please enter record(s) unique ID.')
        arg = self._regex1.findall(arg)
        if not arg:
            raise ValueError('Please enter coherent record(s) unique ID.')
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
        self._arguments["artist"] = arg

    # -----
    # YEAR.
    # -----
    @property
    def year(self):
        return self._year

    @year.setter
    def year(self, arg):
        if not self._regex2.match(arg):
            raise ValueError('Please enter coherent year.')
        self._year = int(arg)
        self._arguments["year"] = int(arg)

    # ------
    # ALBUM.
    # ------
    @property
    def album(self):
        return self._album

    @album.setter
    def album(self, arg):
        self._album = arg
        self._arguments["album"] = arg

    # ----
    # UPC.
    # ----
    @property
    def upc(self):
        return self._upc

    @upc.setter
    def upc(self, arg):
        if not self._regex4.match(arg):
            raise ValueError('Please enter coherent UPC.')
        self._upc = arg
        self._arguments["upc"] = arg

    # ------
    # GENRE.
    # ------
    @property
    def genre(self):
        return self._genre

    @genre.setter
    def genre(self, arg):
        self._genre = arg
        self._arguments["genre"] = arg

    # ----------
    # ALBUMSORT.
    # ----------
    @property
    def albumsort(self):
        return self._albumsort

    @albumsort.setter
    def albumsort(self, arg):
        if not self._regex3.match(choice):
            raise ValueError('Please enter coherent albumsort.')
        self._albumsort = arg
        self._arguments["albumsort"] = arg

    # -----------
    # ARTISTSORT.
    # -----------
    @property
    def artistsort(self):
        return self._artistsort

    @artistsort.setter
    def artistsort(self, arg):
        self._artistsort = arg
        self._arguments["artistsort"] = arg


# ===============
# Main algorithm.
# ===============
if __name__ == "__main__":

    # --> Logging interface.
    with open(os.path.join(os.path.expandvars("%_COMPUTING%"), "logging.yml"), encoding="UTF_8") as fp:
        dictConfig(yaml.load(fp))
    logger = logging.getLogger("Default.{0}".format(os.path.splitext(os.path.basename(__file__))[0]))

    # --> User interface.
    gui = interface(Interface())

    # --> Log arguments.
    logger.debug(gui.database)
    logger.debug(gui.uid)
    for tup in gui.arguments.items():
        logger.debug("{t[0]}: {t[1]}".format(t=tup))
        logger.debug(type(tup[1]))
    sys.exit(update(*gui.uid, db=gui.database, **gui.arguments))
