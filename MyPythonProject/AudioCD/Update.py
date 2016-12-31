# -*- coding: utf-8 -*-
import os
import re
import sys
import yaml
import logging
from Applications import shared
from logging.config import dictConfig
from Applications.Database.AudioCD.shared import update
from Applications.descriptors import Database, Integer

__author__ = 'Xavier ROSSET'


# ========
# Classes.
# ========
class LocalInterface(shared.GlobalInterface):

    # Data descriptor(s).
    database = Database()
    uid = Integer()

    # Regular expression(s).
    _regex1 = re.compile(r"^(?:{0})$".format(shared.DFTYEARREGEX))
    _regex2 = re.compile(r"^1\.(?:{0})0000\.\d$".format(shared.DFTYEARREGEX))
    _regex3 = re.compile(r"\d{12,13}")

    # Instance method(s).
    def __init__(self, *args):
        super(LocalInterface, self).__init__(*args)
        self._upc = None
        self._album = None
        self._genre = None
        self._artist = None
        self._albumsort = None
        self._artistsort = None

    # -------
    # ARTIST.
    # -------
    @property
    def artist(self):
        return self._artist

    @artist.setter
    def artist(self, arg):
        if arg:
            self._artist = arg

    # -----
    # YEAR.
    # -----
    @property
    def year(self):
        return self._year

    @year.setter
    def year(self, arg):
        if arg:
            if not self._regex1.match(arg):
                raise ValueError('Please enter coherent year.')
            self._year = int(arg)

    # ------
    # ALBUM.
    # ------
    @property
    def album(self):
        return self._album

    @album.setter
    def album(self, arg):
        if arg:
            self._album = arg

    # ----
    # UPC.
    # ----
    @property
    def upc(self):
        return self._upc

    @upc.setter
    def upc(self, arg):
        if arg:
            if not self._regex3.match(arg):
                raise ValueError('Please enter coherent UPC.')
            self._upc = arg

    # ------
    # GENRE.
    # ------
    @property
    def genre(self):
        return self._genre

    @genre.setter
    def genre(self, arg):
        if arg:
            self._genre = arg

    # ----------
    # ALBUMSORT.
    # ----------
    @property
    def albumsort(self):
        return self._albumsort

    @albumsort.setter
    def albumsort(self, arg):
        if arg:
            if not self._regex2.match(arg):
                raise ValueError('Please enter coherent albumsort.')
            self._albumsort = arg

    # -----------
    # ARTISTSORT.
    # -----------
    @property
    def artistsort(self):
        return self._artistsort

    @artistsort.setter
    def artistsort(self, arg):
        if arg:
            self._artistsort = arg


# ===============
# Main algorithm.
# ===============
if __name__ == "__main__":

    # --> Logging interface.
    with open(os.path.join(os.path.expandvars("%_COMPUTING%"), "logging.yml"), encoding="UTF_8") as fp:
        dictConfig(yaml.load(fp))
    logger = logging.getLogger("Default.{0}".format(os.path.splitext(os.path.basename(__file__))[0]))

    # --> User interface.
    gui = shared.interface(LocalInterface([("Please enter database to update", "database"), 
                                           ("Please enter record(s) unique ID", "uid"),
                                           ("Please enter artist new value ", "artist"),
                                           ("Please enter year new value", "year"),
                                           ("Please enter album new value", "album"),
                                           ("Please enter UPC new value", "upc"),
                                           ("Please enter genre new value", "genre"),
                                           ("Please enter albumsort new value", "albumsort"),
                                           ("Please enter artistsort new value", "artistsort")]
                                          )
                           )

    # --> Log arguments.
    logger.debug(gui.database)
    logger.debug(gui.uid)
    arguments = {i: getattr(gui, i) for i in ["artist", "year", "album", "upc", "genre", "albumsort", "artistsort"] if hasattr(gui, i) and getattr(gui, i) is not None}
    if arguments:
        for tup in arguments.items():
            logger.debug("{t[0]}: {t[1]}".format(t=tup))
        sys.exit(update(*gui.uid, db=gui.database, **arguments))
    sys.exit(0)
