# -*- coding: ISO-8859-1 -*-
__author__ = 'Xavier ROSSET'


# =================
# Absolute imports.
# =================
from sortedcontainers import SortedDict
from datetime import datetime
from pytz import timezone
import logging
import json
import os
import re


# =================
# Relative imports.
# =================
from ... import shared


# ==========
# Constants.
# ==========
DFTPATTERN = r"^(?:\ufeff)?(?!#)(?:z_)?([^=]+)=(.+)$"
PROFILES = ["default", "defaultbootlegs", "pjbootlegs", "selftitled"]
GENRES = os.path.join(os.path.expandvars("%_PYTHONPROJECT%"), "Applications", "CDRipper", "Genres.json")
LANGUAGES = os.path.join(os.path.expandvars("%_PYTHONPROJECT%"), "Applications", "CDRipper", "Languages.json")
ENCODERS = os.path.join(os.path.expandvars("%_PYTHONPROJECT%"), "Applications", "CDRipper", "Encoders.json")
TITLES = os.path.join(os.path.expandvars("%_COMPUTING%"), "Titles.json")
ENC_KEYS = ["name", "code", "folder", "extension"]
TIT_KEYS = ["number", "title", "overwrite"]


# ========
# Logging.
# ========
logger = logging.getLogger("%s.%s" % (__package__, os.path.basename(__file__)))


# ========
# Classes.
# ========
# http://stackoverflow.com/questions/31909094/overriding-an-inherited-property-setter
class AudioCD(MutableMappings):
    itags = ["artist", "title", "track", "disc", "upc", "profile", "source", "incollection", "titlelanguage", "genre", "artistsort", "albumartist", "albumartistsort", "_albumart_1_front album cover", "style"]
             # "encoder"]
    # otags = ["artist", "title", "track", "disc", "upc", "profile", "source", "incollection", "titlelanguage", "genre", "artistsort", "albumartist", "albumartistsort", "_albumart_1_front album cover", "style",
             # "encodedby", "taggingtime", "encodingtime", "encodingyear"]

    def __getitem__(self, itm):
        return self.otags[itm]

    def __setitem__(self, key, value):
        return self.otags[key] = value

    def __delitem__(self, itm):
        del self.otags[itm]

    def __len__(self):
        return len(self.otags)

    def __iter__(self):
        return iter(self.otags)

    def __init__(self, **kwargs):
        self._otags = dict()
        self.otags = kwargs

    def digitalaudiobase(self):
        l = list()
        l.append("{artistsort[:1]}.{artistsort}.{albumsort[:-3]}.{titlesort}".format(**self.otags))
        l.append(self.otags["albumsort"][:-3])
        l.extends([self.otags[key] for key in ["titlesort", "artist", "year", "album", "genre", "discnumber", "totaldiscs", "label", "tracknumber", "totaltracks", "title", "live", "bootleg", "incollection", "upc", "encodingyear", "titlelanguage", "origyear"]])
        for item in l:
            yield l

    @property
    def otags(self):
        return self._otags

    @otags.setter
    def otags(self, **kwargs):

        if "artist" not in kwargs:
            raise TagError
        if "track" not in kwargs:
            raise TagError
        if "disc" not in kwargs:
            raise TagError
        if "encoder" not in kwargs:
            raise TagError

        # ----- Attributes taken from the input file.
        self._otags = {key: kwargs[key] for key in kwargs if key in AudioCD.itags}

        # ----- Encodedby.
        self._otags["encodedby"] = "dBpoweramp 15.1 on {0}".format(shared.dateformat(datetime.now(tz=timezone(shared.DFTTIMEZONE)), shared.TEMPLATE3))

        # ----- Taggingtime.
        self._otags["taggingtime"] = shared.dateformat(datetime.now(tz=timezone(shared.DFTTIMEZONE)), shared.TEMPLATE3)

        # ----- Encodingtime.
        self._otags["encodingtime"] = int(datetime.now(tz=timezone(shared.DFTTIMEZONE)).timestamp())
        self._otags["encodingyear"] = datetime.now(tz=timezone(shared.DFTTIMEZONE)).strftime("%Y")

        # ----- Encoder attributes.
        for encoder in self.deserialize(ENCODERS):  # "encoder" est un dictionnaire.
            if sorted(list(encoder.keys())) == sorted(ENC_KEYS):
                if kwargs["encoder"] == encoder["name"]:
                    self._otags["encoder"] = nt(encoder["name"], encoder["code"], encoder["folder"], encoder["extension"])
                    logger.debug("Used encoder.")
                    logger.debug("\t%s".expandtabs(4) % ("Name\t: %s".expandtabs(9) % (encoder["name"],)),)
                    logger.debug("\t%s".expandtabs(4) % ("Code\t: %s".expandtabs(9) % (encoder["code"],)),)
                    logger.debug("\t%s".expandtabs(4) % ("Folder\t: %s".expandtabs(9) % (encoder["folder"],)),)
                    logger.debug("\t%s".expandtabs(4) % ("Extension: %s" % (encoder["extension"],)),)
                    break

        # ----- Tracknumber / Totaltracks.
        self._otags["tracknumber"], self._otags["totaltracks"] = self.splitfield(kwargs["track"], r"^(\d{1,2})/(\d{1,2})")

        # ----- Discnumber / Totaldiscs.
        self._otags["discnumber"], self._otags["totaldiscs"] = self.splitfield(kwargs["disc"], r"^(\d{1,2})/(\d{1,2})")

        # ----- Genre.
        for artist, genre in self.deserialize(GENRES):
            if kwargs["artist"].lower() == artist.lower():
                self._otags["genre"] = genre
                break

        # ----- Titlelanguage.
        for artist, language in self.deserialize(LANGUAGES):
            if kwargs["artist"].lower() == artist.lower():
                self._otags["language"] = language
                break

        # ----- Title.
        for track in self.deserialize(TITLES):  # "track" est un dictionnaire.
            if sorted(list(track.keys())) == sorted(TIT_KEYS):
                if self._otags["tracknumber"] == track["number"]:
                    if track["overwrite"]:
                        self._otags["title"] = track["title"]
                        break

    @classmethod
    def fromfile(cls, fil, enc=shared.UTF8):
        regex, d = re.compile(DFTPATTERN, re.IGNORECASE), {}
        with open(fil, encoding=enc) as f:
            for line in cls.contents(f):
                match = regex.match(line)
                if match:
                    d[match.group(1).rstrip().lower()] = match.group(2)
        return cls(**SortedDict(d))

    @classmethod
    def case(cls, s):
        regex = {"1": r"(for|and|nor|but|or|yet|so)",
                 "2": r"((?:al)?though|as|because|if|since|so that|such as|to|unless|until|when|where(?:as)?|while)",
                 "3": r"(above|after|against|along(?:side)?|around|at|before|behind|below|between|beside|close to|down|(?:far )?from|in(?: front of)?(?:side)?(to)?|near|off?|on(?:to)?|out(?:side)?|over|toward|"
                      r"under(?:neath)?|up(?: to)?)",
                 "4": r"(a(?:n(?:d)?)?|as|by|than|the|till|upon)",
                 "5": r"[\.\-]+"}

        # ---------------------------------------------
        # Chaque mot est formaté en lettres minuscules.
        # ---------------------------------------------
        s = re.compile(r"(?i)^(.+)$").sub(cls.low, s)

        # --------------------------
        # Chaque mot est capitalisé.
        # --------------------------
        s = re.compile(r"(?i)\b([a-z]+)\b").sub(cls.cap1, s)

        # -------------------------------------------------------------
        # Les conjonctions demeurent entièrement en lettres minsucules.
        # -------------------------------------------------------------
        s = re.compile(r"(?i)\b{0}\b".format(regex["1"])).sub(cls.low, s)
        s = re.compile(r"(?i)\b{0}\b".format(regex["2"])).sub(cls.low, s)
        s = re.compile(r"(?i)\b{0}\b".format(regex["3"])).sub(cls.low, s)
        s = re.compile(r"(?i)\b{0}\b".format(regex["4"])).sub(cls.low, s)

        # -------------------------------------
        # Le début du titre demeure capitalisé.
        # -------------------------------------
        s = re.compile(r"(?i)^{0}\b".format(regex["1"])).sub(cls.cap1, s)
        s = re.compile(r"(?i)^{0}\b".format(regex["2"])).sub(cls.cap1, s)
        s = re.compile(r"(?i)^{0}\b".format(regex["3"])).sub(cls.cap1, s)
        s = re.compile(r"(?i)^{0}\b".format(regex["4"])).sub(cls.cap1, s)
        s = re.compile(r"(?i)^({0})({1})\b".format(regex["5"], regex["1"])).sub(cls.cap2, s)
        s = re.compile(r"(?i)^({0})({1})\b".format(regex["5"], regex["2"])).sub(cls.cap2, s)
        s = re.compile(r"(?i)^({0})({1})\b".format(regex["5"], regex["3"])).sub(cls.cap2, s)
        s = re.compile(r"(?i)^({0})({1})\b".format(regex["5"], regex["4"])).sub(cls.cap2, s)

        # ------------------------------------
        # Les acronymes demeurent capitalisés.
        # ------------------------------------
        s = re.compile(r"(?i)\b(u\.?s\.?a\.?)").sub(cls.upp, s)
        s = re.compile(r"(?i)\b(u\.?k\.?)").sub(cls.upp, s)
        s = re.compile(r"(?i)\b(dj)\b").sub(cls.upp, s)

        # ----------------------------------
        # Autres mots demeurant capitalisés.
        # ----------------------------------
        s = re.compile(r"(?i)\b({0})({1})\b".format(regex["5"], regex["3"])).sub(cls.cap2, s)

        # -----------------------------------------------------------------
        # Les mots précédés d'une apostrophe demeurent en lettre minuscule.
        #  ----------------------------------------------------------------
        s = re.compile(r"(?i)\b('[a-z])\b").sub(cls.low, s)

        # ------------------
        # Autres formatages.
        # ------------------
        s = re.compile(r"(?i)\bfeaturing\b").sub("feat.", s)
        s = re.compile(r"(?i)^([^\[]+)\[([^\]]+)\]$").sub(cls.parenth, s)

        # -------
        # Return.
        # -------
        return s

    @staticmethod
    def contents(fil):
        for line in fil:
            if line.startswith("#"):
                continue
            if not line:
                continue
            yield line

    @staticmethod
    def splitfield(fld, rex):
        m = re.compile(rex).match(fld)
        if m:
            return m.group(1, 2)
        return ()

    @staticmethod
    def cap1(s):
        """
        Get a regular expression match object and capitalize the first capturing group.
        :param s: match object.
        :return: formatted capturing group(s).
        """
        return s.groups()[0].capitalize()

    @staticmethod
    def cap2(s):
        """
        Get a regular expression match object and concatenate its first two capturing groups. Second group is capitalized.
        :param s: match object.
        :return: formatted capturing group(s).
        """
        return "{0}{1}".format(s.groups()[0], s.groups()[1].capitalize())

    @staticmethod
    def upp(s):
        """
        Get a regular expression match object and set the first capturing group to uppercase.
        :param s: match object.
        :return: formatted capturing group(s).
        """
        return s.groups()[0].upper()

    @staticmethod
    def low(s):
        """
        Get a regular expression match object and set the first capturing group to lowercase.
        :param s: match object.
        :return: formatted capturing group(s).
        """
        return s.groups()[0].lower()

    @staticmethod
    def parenth(s):
        """
        Get a regular expression match object and concatenate its first two capturing groups. Second group is parenthesised.
        :param s: match object.
        :return: formatted capturing group(s).
        """
        return "{d[0]}({d[1]})".format(d=s.groups())

    @staticmethod
    def deserialize(fil, enc=shared.UTF8):
        with open(fil, encoding=enc) as fp:
            for structure in json.load(fp):
                yield structure


class DefaultCD(AudioCD):
    itags = ["label", "year", "album", "origyear", "albumsortcount", "bootleg", "live"]
    # otags = ["label", "year", "album", "origyear", "albumsort", "titlesort"]

    def __init__(self, **kwargs):
        super(DefaultCD, self).__init__(**kwargs)
        DefaultCD.otags.fset(self, kwargs)

    @AudioCD.otags.setter
    def otags(self, kwargs):

        self._otags = {key: kwargs[key] for key in kwargs if key in DefaultCD.itags}

        # ----- Album.
        self._otags["album"] = self.case(self.album)

        # ----- Albumsort.
        if not missingattribute(self, *("year",)):
            self.albumsortyear = self.year
        if not missingattribute(self, *("origyear",)):
            self.albumsortyear = self.origyear
        if not missingattribute(self, *("albumsortyear", "albumsortcount", "encodercode")):
            self.albumsort = "1.{year}0000.{count}.{enc}".format(year=self.albumsortyear, count=self.albumsortcount, enc=self.encodercode)
        logger.debug("Build tags.")
        logger.debug("\talbumsort: %s".expandtabs(4) % (self.albumsort,))

        # ----- Titlesort.
        if not missingattribute(self, *("discnumber", "tracknumber", "bonus", "live", "bootleg")):
            self.titlesort = "D{disc}.T{track}.{bonus}{live}{bootleg}".format(disc=self.discnumber, track=self.tracknumber.zfill(2), bonus=self.bonus, live=self.live, bootleg=self.bootleg)


# ==========
# Functions.
# ==========
def missingattribute(obj, *attrs):
    """
    Check if an object has got attribute(s).
    :param obj: object created from AudioCD class.
    :param attrs: attribute(s) looked for.
    :return: True: at lease one attribute is missing.
             False: all attributes looked for are present.
    """
    if all(hasattr(obj, name) for name in attrs):
        return False
    return True


def canfilebeprocessed(fe, *tu):
    """
    fe: file extension.
    tu: filtered extensions tuple.
    """
    if fe.lower() not in ["ape", "flac", "m4a", "mp3", "ogg"]:
        return False
    if not tu:
        return True
    if fe.lower() in [item.lower() for item in tu]:
        return True
    return False
