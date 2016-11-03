# -*- coding: ISO-8859-1 -*-
from collections import MutableMapping, namedtuple
from jinja2 import Environment, FileSystemLoader
from sortedcontainers import SortedDict
from contextlib import ContextDecorator
from datetime import datetime
from pytz import timezone
import logging
import json
import os
import re
from ... import shared

__author__ = 'Xavier ROSSET'


# ========
# Logging.
# ========
logger = logging.getLogger("%s.%s" % (__package__, os.path.basename(__file__)))


# ========
# Classes.
# ========
class AudioCD(MutableMapping):

    tags = {"artistsort": True, "albumartistsort": False, "artist": True, "albumartist": False, "encoder": True, "disc": True, "track": True, "title": False, "profile": False, "source": False, "bootleg": True,
            "live": True, "incollection": True, "titlelanguage": False, "genre": False, "style": False, "rating": False, "_albumart_1_front album cover": False}

    def __init__(self, **kwargs):

        nt = namedtuple("nt", "name code folder extension")
        regex = re.compile(r"^(\d{1,2})/(\d{1,2})")
        self._encoder = None
        self._otags = dict()

        # ----- Check mandatory input tags.
        for item in [item for item in AudioCD.tags if AudioCD.tags[item]]:
            if item not in kwargs:
                raise ValueError("{0} isn\'t available.".format(item))
        if not regex.match(kwargs["track"]):
            raise ValueError("track doesn\'t respect the expected pattern.")
        if not regex.match(kwargs["disc"]):
            raise ValueError("disc doesn\'t respect the expected pattern.")
        if kwargs["encoder"] not in [encoder.get("name") for encoder in self.deserialize(ENCODERS)]:
            raise ValueError('"{0}" as encoder isn\'t recognized.'.format(kwargs["encoder"]))

        # ----- Attributes taken from the input tags.
        self._otags = {key: kwargs[key] for key in kwargs if key in AudioCD.tags}

        # ----- Set encodedby.
        self._otags["encodedby"] = "dBpoweramp 15.1 on {0}".format(shared.dateformat(datetime.now(tz=timezone(shared.DFTTIMEZONE)), shared.TEMPLATE3))

        # ----- Set taggingtime.
        self._otags["taggingtime"] = shared.dateformat(datetime.now(tz=timezone(shared.DFTTIMEZONE)), shared.TEMPLATE3)

        # ----- Set encodingtime.
        self._otags["encodingtime"] = int(datetime.now(tz=timezone(shared.DFTTIMEZONE)).timestamp())
        self._otags["encodingyear"] = datetime.now(tz=timezone(shared.DFTTIMEZONE)).strftime("%Y")

        # ----- Set encoder attributes.
        for encoder in self.deserialize(ENCODERS):  # "encoder" est un dictionnaire.
            if sorted(list(encoder.keys())) == sorted(ENC_KEYS):
                if kwargs["encoder"] == encoder["name"]:
                    self._otags["encoder"] = kwargs["encoder"]
                    self._encoder = nt(encoder["name"], encoder["code"], encoder["folder"], encoder["extension"])
                    logger.debug("Used encoder.")
                    logger.debug("\t%s".expandtabs(4) % ("Name\t: %s".expandtabs(9) % (self._encoder.name,)),)
                    logger.debug("\t%s".expandtabs(4) % ("Code\t: %s".expandtabs(9) % (self._encoder.code,)),)
                    logger.debug("\t%s".expandtabs(4) % ("Folder\t: %s".expandtabs(9) % (self._encoder.folder,)),)
                    logger.debug("\t%s".expandtabs(4) % ("Extension: %s" % (self._encoder.extension,)),)
                    break

        # ----- Both update track and set total tracks.
        self._otags["track"], self._otags[MAPPING.get(kwargs["encoder"], MAPPING["default"])["totaltracks"]] = self.splitfield(kwargs["track"], regex)

        # ----- Both update disc and set total discs.
        self._otags["disc"], self._otags[MAPPING.get(kwargs["encoder"], MAPPING["default"])["totaldiscs"]] = self.splitfield(kwargs["disc"], regex)

        # ----- Update genre.
        for artist, genre in self.deserialize(GENRES):
            if kwargs["artist"].lower() == artist.lower():
                self._otags["genre"] = genre
                break

        # ----- Update titlelanguage.
        for artist, language in self.deserialize(LANGUAGES):
            if kwargs["artist"].lower() == artist.lower():
                self._otags["titlelanguage"] = language
                break

        # ----- Update title.
        for track in self.deserialize(TITLES):  # "track" est un dictionnaire.
            if sorted(list(track.keys())) == sorted(TIT_KEYS):
                if self._otags["track"] == track["number"]:
                    if track["overwrite"]:
                        self._otags["title"] = track["title"]
                        break

    def __getitem__(self, item):
        return self._otags[item]

    def __setitem__(self, key, value):
        self._otags[key] = value

    def __delitem__(self, key):
        del self._otags[key]

    def __len__(self):
        return len(self._otags)

    def __iter__(self):
        return iter(self._otags)

    @property
    def encoder(self):
        return self._otags["encoder"]

    @property
    def index(self):
        return "{0}.{1}.{2}.{3}".format(self._otags["artistsort"][:1], self._otags["artistsort"], self._otags["albumsort"][:-3], self._otags["titlesort"])

    @property
    def artistsort(self):
        return self._otags["artistsort"]

    @property
    def albumsort(self):
        return self._otags["albumsort"]

    @property
    def titlesort(self):
        return self._otags["titlesort"]

    @property
    def discnumber(self):
        return self._otags["disc"]

    @property
    def totaldiscs(self):
        return self._otags[MAPPING.get(self.encoder, MAPPING["default"])["totaldiscs"]]

    @property
    def tracknumber(self):
        return self._otags["track"]

    @property
    def totaltracks(self):
        return self._otags[MAPPING.get(self.encoder, MAPPING["default"])["totaltracks"]]

    @property
    def artist(self):
        return self._otags["artist"]

    @property
    def origyear(self):
        return self._otags["origyear"]

    @property
    def year(self):
        return self._otags["year"]

    @property
    def album(self):
        return self._otags["album"]

    @property
    def title(self):
        return self._otags["title"]

    @property
    def genre(self):
        return self._otags["genre"]

    @property
    def titlelanguage(self):
        return self._otags["titlelanguage"]

    @property
    def label(self):
        return self._otags["label"]

    @property
    def upc(self):
        return self._otags["upc"]

    @property
    def live(self):
        return self._otags["live"]

    @property
    def bootleg(self):
        return self._otags["bootleg"]

    @property
    def incollection(self):
        return self._otags["incollection"]

    @property
    def encodingyear(self):
        return self._otags["encodingyear"]

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
        m = rex.match(fld)
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

    tags = {"origyear": False, "year": True, "albumsortcount": True, "album": True, "upc": True, "label": True}

    def __init__(self, **kwargs):
        super(DefaultCD, self).__init__(**kwargs)

        # ----- Check mandatory input tags.
        for item in [item for item in DefaultCD.tags if DefaultCD.tags[item]]:
            if item not in kwargs:
                raise ValueError("{0} isn\'t available.".format(item))

        # ----- Update tags.
        self._otags.update({key: kwargs[key] for key in kwargs if key in DefaultCD.tags})

        # ----- Update album.
        self._otags["album"] = self.case(kwargs["album"])

        # ----- Set albumsort.
        self._otags["albumsort"] = "1.{year}0000.{count}.{enc}".format(year=kwargs.get("origyear", kwargs["year"]), count=kwargs["albumsortcount"], enc=self._encoder.code)

        # ----- Set titlesort.
        self._otags["titlesort"] = "D{disc}.T{track}.{bonus}{live}{bootleg}".format(disc=self._otags["disc"],
                                                                                    track=self._otags["track"].zfill(2),
                                                                                    bonus="N",
                                                                                    live=self._otags["live"],
                                                                                    bootleg=self._otags["bootleg"])

        # ----- Update origyear.
        self._otags["origyear"] = kwargs.get("origyear", kwargs["year"])

        # ----- Log new tags.
        logger.debug("Build tags.")
        logger.debug("\talbum    : %s".expandtabs(4) % (self._otags["album"],))
        logger.debug("\talbumsort: %s".expandtabs(4) % (self._otags["albumsort"],))
        logger.debug("\ttitlesort: %s".expandtabs(4) % (self._otags["titlesort"],))
        logger.debug("\torigyear : %s".expandtabs(4) % (self._otags["origyear"],))


class SelfTitledCD(DefaultCD):

    itags = []

    def __init__(self, **kwargs):
        super(SelfTitledCD, self).__init__(**kwargs)

        # ----- Check mandatory input tags.
        for item in [item for item in SelfTitledCD.tags if SelfTitledCD.tags[item]]:
            if item not in kwargs:
                raise ValueError("{0} isn\'t available.".format(item))

        # ----- Update tags.
        self._otags.update({key: kwargs[key] for key in kwargs if key in SelfTitledCD.itags})

        # ----- Update album.
        self._otags["album"] = "{0} (Self Titled)".format(kwargs["year"])


class RippedCD(ContextDecorator):

    environment = Environment(loader=FileSystemLoader(os.path.join(os.path.expandvars("%_PYTHONPROJECT%"), "Applications", "CDRipper", "Templates")), trim_blocks=True, lstrip_blocks=True)
    outputtags = environment.get_template("AudioCDOutputTags")

    def __init__(self, ripprofile, tagsfile, test=True):
        self._rippedcd = None
        self._profile = None
        self._tags = None
        self._test = None
        self.profile = ripprofile
        self.tags = tagsfile
        self.test = test

    @property
    def profile(self):
        return self._profile

    @profile.setter
    def profile(self, arg):
        if arg.lower() not in PROFILES:
            raise ValueError('"{0}" isn\'t allowed.'.format(arg.lower()))
        self._profile = arg

    @property
    def tags(self):
        return self._tags

    @tags.setter
    def tags(self, arg):
        if not os.path.exists(arg):
            raise ValueError('"{0}" doesn\'t exist.'.format(arg))
        self._tags = arg

    @property
    def test(self):
        return self._test

    @test.setter
    def test(self, arg):
        self._test = arg

    @property
    def new(self):
        return self._rippedcd

    def __enter__(self):

        # --> 1. Start logging.
        logger.debug("{0:=^140}".format(" {0} ".format(shared.dateformat(datetime.now(tz=timezone(shared.DFTTIMEZONE)), shared.TEMPLATE1))))
        logger.debug('START "%s".' % (os.path.basename(__file__),))
        logger.debug('"{0}" used as ripping profile.'.format(self.profile))

        # --> 2. Log input tags.
        logger.debug("Input file.")
        logger.debug('\t"{0}"'.format(self.tags).expandtabs(4))
        logger.debug("Input tags.")
        if os.path.exists(self.tags):
            with open(self.tags, encoding=shared.UTF16) as fr:
                for line in fr:
                    logger.debug("\t{0}".format(line.splitlines()[0]).expandtabs(4))

        # --> 3. Create AudioCD instance.
        self._rippedcd = PROFILES[self.profile].isinstancedfrom(self.tags, shared.UTF16)  # l'attribut "_rippedcd" est une instance de type "AudioCD".

        # --> 4. Return instance.
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):

        # --> 1. Log output tags.
        logger.debug("Output tags.")
        for k, v in self.new.items():
            logger.debug("\t{0}={1}".format(k, v).expandtabs(4))

        # --> 2. Store tags.
        fo, encoding = self.tags, shared.UTF16
        if self.test:
            fo, encoding = os.path.join(os.path.expandvars("%TEMP%"), "T{0}.txt".format(self.new.tracknumber.zfill(2))), shared.UTF8
        with open(fo, shared.WRITE, encoding=encoding) as fw:
            logger.debug("Tags file.")
            logger.debug("\t{0}".format(fo).expandtabs(4))
            fw.write(self.outputtags.render(tags={key: self.new[key] for key in self.new if key not in PROFILES[self.profile].exclusions}))

        # --> 3. Store tags in JSON.
        JSON, obj = os.path.join(os.path.expandvars("%TEMP%"), "tags.json"), []
        if os.path.exists(JSON):
            with open(JSON) as fp:
                obj = json.load(fp)
        obj.append(dict(self.new))
        with open(JSON, shared.WRITE) as fp:
            json.dump(obj, fp, indent=4, sort_keys=True)

        # --> 4. Stop logging.
        logger.debug('END "%s".' % (os.path.basename(__file__),))


# ==========
# Functions.
# ==========
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


# ================
# Initializations.
# ================
profile = namedtuple("profile", "exclusions isinstancedfrom")


# ==========
# Constants.
# ==========
DFTPATTERN = r"^(?:\ufeff)?(?!#)(?:z_)?([^=]+)=(.+)$"
GENRES = os.path.join(os.path.expandvars("%_PYTHONPROJECT%"), "Applications", "CDRipper", "Genres.json")
LANGUAGES = os.path.join(os.path.expandvars("%_PYTHONPROJECT%"), "Applications", "CDRipper", "Languages.json")
ENCODERS = os.path.join(os.path.expandvars("%_PYTHONPROJECT%"), "Applications", "CDRipper", "Encoders.json")
TITLES = os.path.join(os.path.expandvars("%_COMPUTING%"), "Titles.json")
ENC_KEYS = ["name", "code", "folder", "extension"]
TIT_KEYS = ["number", "title", "overwrite"]
PROFILES = {"default": profile(["albumsortcount", "bootleg", "live"], DefaultCD.fromfile),
            "default1": profile(["albumsortcount", "bootleg", "live"], DefaultCD.fromfile),
            "selftitled": profile(["albumsortcount", "bootleg", "live"], SelfTitledCD.fromfile)}
with open(os.path.join(os.path.expandvars("%_PYTHONPROJECT%"), r"Applications/CDRipper/Mapping.json")) as fp:
    MAPPING = json.load(fp)
