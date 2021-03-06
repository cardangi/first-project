# -*- coding: utf-8 -*-
from collections import MutableMapping, namedtuple
from contextlib import ContextDecorator, ExitStack
from jinja2 import Environment, FileSystemLoader
from collections import MutableSequence
from sortedcontainers import SortedDict
from mutagen.apev2 import APETextValue
from mutagen.easyid3 import EasyID3
from operator import itemgetter
from itertools import compress
from datetime import datetime
from base64 import b85decode
import mutagen.monkeysaudio
from pytz import timezone
import ftputil.error
import mutagen.flac
import mutagen.mp3
import itertools
import argparse
import mutagen
import logging
import shutil
import json
import os
import re
from .. import shared

__author__ = 'Xavier ROSSET'


# ========
# Classes.
# ========
class AudioCDTrack(MutableMapping):

    tags = {"artistsort": True, "albumartistsort": False, "artist": True, "albumartist": False, "encoder": True, "disc": True, "track": True, "title": False, "profile": False, "source": False, "bootleg": True,
            "live": True, "incollection": True, "titlelanguage": False, "genre": False, "style": False, "rating": False, "_albumart_1_front album cover": False}
    logger = logging.getLogger("{0}.AudioCDTrack".format(__name__))

    def __init__(self, **kwargs):

        nt = namedtuple("nt", "name code folder extension")
        regex = re.compile(r"^(\d{1,2})/(\d{1,2})")
        self._encoder = None
        self._otags = dict()

        # ----- Check mandatory input tags.
        for item in (item for item in AudioCDTrack.tags if AudioCDTrack.tags[item]):
            if item not in kwargs:
                raise ValueError("{0} isn\'t available.".format(item))
        if not regex.match(kwargs["track"]):
            raise ValueError("track doesn\'t respect the expected pattern.")
        if not regex.match(kwargs["disc"]):
            raise ValueError("disc doesn\'t respect the expected pattern.")
        if kwargs["encoder"] not in [encoder.get("name") for encoder in self.deserialize(ENCODERS)]:
            raise ValueError('"{0}" as encoder isn\'t recognized.'.format(kwargs["encoder"]))

        # ----- Attributes taken from the input tags.
        self._otags = {key: kwargs[key] for key in kwargs if key in AudioCDTrack.tags}

        # ----- Set encodedby.
        self.logger.debug("Set encodedby.")
        self._otags["encodedby"] = "dBpoweramp 15.1 on {0}".format(shared.dateformat(datetime.now(tz=timezone(shared.DFTTIMEZONE)), shared.TEMPLATE3))

        # ----- Set taggingtime.
        self.logger.debug("Set taggingtime.")
        self._otags["taggingtime"] = shared.dateformat(datetime.now(tz=timezone(shared.DFTTIMEZONE)), shared.TEMPLATE3)

        # ----- Set encodingtime.
        self.logger.debug("Set encodingtime.")
        self._otags["encodingtime"] = int(datetime.now(tz=timezone(shared.DFTTIMEZONE)).timestamp())

        # ----- Set encodingyear.
        self.logger.debug("Set encodingyear.")
        self._otags["encodingyear"] = datetime.now(tz=timezone(shared.DFTTIMEZONE)).strftime("%Y")

        # ----- Set encoder attributes.
        self.logger.debug("Set encoder attributes.")
        for encoder in self.deserialize(ENCODERS):  # "encoder" est un dictionnaire.
            if sorted(encoder) == sorted(ENC_KEYS):
                if kwargs["encoder"] == encoder["name"]:
                    self._otags["encoder"] = kwargs["encoder"]
                    self._encoder = nt(encoder["name"], encoder["code"], encoder["folder"], encoder["extension"])
                    self.logger.debug("Used encoder.")
                    self.logger.debug("\t%s".expandtabs(4) % ("Name\t: %s".expandtabs(9) % (self._encoder.name,)),)
                    self.logger.debug("\t%s".expandtabs(4) % ("Code\t: %s".expandtabs(9) % (self._encoder.code,)),)
                    self.logger.debug("\t%s".expandtabs(4) % ("Folder\t: %s".expandtabs(9) % (self._encoder.folder,)),)
                    self.logger.debug("\t%s".expandtabs(4) % ("Extension: %s" % (self._encoder.extension,)),)
                    break

        # ----- Both update track and set total tracks.
        self.logger.debug("Set track.")
        self._otags["track"], self._otags[MAPPING.get(kwargs["encoder"], MAPPING["default"])["totaltracks"]] = self.splitfield(kwargs["track"], regex)

        # ----- Both update disc and set total discs.
        self.logger.debug("Set disc.")
        self._otags["disc"], self._otags[MAPPING.get(kwargs["encoder"], MAPPING["default"])["totaldiscs"]] = self.splitfield(kwargs["disc"], regex)

        # ----- Update genre.
        self.logger.debug("Update genre.")
        for artist, genre in self.deserialize(GENRES):
            if kwargs["artist"].lower() == artist.lower():
                self._otags["genre"] = genre
                break

        # ----- Update titlelanguage.
        self.logger.debug("Update titlelanguage.")
        for artist, language in self.deserialize(LANGUAGES):
            if kwargs["artist"].lower() == artist.lower():
                self._otags["titlelanguage"] = language
                break

        # ----- Update title.
        self.logger.debug("Update title.")
        for track in self.deserialize(TITLES):  # "track" est un dictionnaire.
            if sorted(track) == sorted(TIT_KEYS):
                if self._otags["track"] == track["number"]:
                    if track["overwrite"]:
                        self._otags["title"] = track["title"]
                        break
        self._otags["title"] = self.case(self._otags["title"])

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
    def bonus(self):
        return self._otags.get("bonus", "N")

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
            for line in filcontents(f):
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
        with open(fil, encoding=enc) as fr:
            for structure in json.load(fr):
                yield structure


class DefaultCDTrack(AudioCDTrack):

    tags = {"origyear": False, "year": True, "albumsortcount": True, "album": True, "upc": True, "label": True, "bonus": False}
    logger = logging.getLogger("{0}.DefaultCDTrack".format(__name__))

    def __init__(self, **kwargs):
        super(DefaultCDTrack, self).__init__(**kwargs)

        # ----- Check mandatory input tags.
        for item in (item for item in DefaultCDTrack.tags if DefaultCDTrack.tags[item]):
            if item not in kwargs:
                raise ValueError("{0} isn\'t available.".format(item))

        # ----- Update tags.
        self._otags.update({key: kwargs[key] for key in kwargs if key in DefaultCDTrack.tags})

        # ----- Set origyear.
        self.logger.debug("Set origyear.")
        self._otags["origyear"] = self._otags.get("origyear", self._otags["year"])

        # ----- Set albumsort.
        self.logger.debug("Set albumsort.")
        self._otags["albumsort"] = "1.{year}0000.{uid}.{enc}".format(year=self._otags["origyear"], uid=self._otags["albumsortcount"], enc=self._encoder.code)

        # ----- Set titlesort.
        self.logger.debug("Set titlesort.")
        self._otags["titlesort"] = "D{disc}.T{track}.{bonus}{live}{bootleg}".format(disc=self._otags["disc"],
                                                                                    track=self._otags["track"].zfill(2),
                                                                                    bonus=self._otags.get("bonus", "N"),
                                                                                    live=self._otags["live"],
                                                                                    bootleg=self._otags["bootleg"])

        # ----- Update album.
        self.logger.debug("Update album.")
        self._otags["album"] = self.case(self._otags["album"])

        # ----- Log new tags.
        self.logger.debug("Build tags.")
        self.logger.debug("\talbum    : %s".expandtabs(4) % (self._otags["album"],))
        self.logger.debug("\talbumsort: %s".expandtabs(4) % (self._otags["albumsort"],))
        self.logger.debug("\ttitlesort: %s".expandtabs(4) % (self._otags["titlesort"],))
        self.logger.debug("\torigyear : %s".expandtabs(4) % (self._otags["origyear"],))


class SelfTitledCDTrack(DefaultCDTrack):

    tags = {}
    logger = logging.getLogger("{0}.SelfTitledCDTrack".format(__name__))

    def __init__(self, **kwargs):
        super(SelfTitledCDTrack, self).__init__(**kwargs)

        # ----- Check mandatory input tags.
        for item in (item for item in SelfTitledCDTrack.tags if SelfTitledCDTrack.tags[item]):
            if item not in kwargs:
                raise ValueError("{0} isn\'t available.".format(item))

        # ----- Update tags.
        self._otags.update({key: kwargs[key] for key in kwargs if key in SelfTitledCDTrack.tags})

        # ----- Update album.
        self.logger.debug("Update album.")
        self._otags["album"] = "{year} (Self Titled)".format(year=self._otags["origyear"])


class BootlegCDTrack(AudioCDTrack):

    tags = {"bootlegtracktour": True, "bootlegtrackyear": True, "bootlegtrackcity": True, "albumsortcount": True, "provider": False, "providerreference": False, "origalbum": False, "groupby": False, "bonus": True}
    rex1 = re.compile(r"\W+")
    rex2 = re.compile(r", ([A-Z][a-z]+)$")
    DFTCOUNTRY = "United States"
    logger = logging.getLogger("{0}.BootlegCDTrack".format(__name__))

    def __init__(self, **kwargs):
        super(BootlegCDTrack, self).__init__(**kwargs)

        # ----- Check mandatory input tags.
        for item in (item for item in BootlegCDTrack.tags if BootlegCDTrack.tags[item]):
            if item not in kwargs:
                raise ValueError("{0} isn\'t available.".format(item))

        # ----- Update tags.
        self._otags.update({key: kwargs[key] for key in kwargs if key in BootlegCDTrack.tags})

        # ----- Update bootlegtrackyear.
        self.logger.debug("Update bootlegtrackyear.")
        self._otags["bootlegtrackyear"] = self.rex1.sub("-", self._otags["bootlegtrackyear"])
        
        # ----- Set bootlegtrackcountry.
        self.logger.debug("Set bootlegtrackcountry.")
        self._otags["bootlegtrackcountry"] = BootlegCDTrack.DFTCOUNTRY
        match = self.rex2.search(self._otags["bootlegtrackcity"])
        if match:
            self._otags["bootlegtrackcountry"] = match.group(1)

        # ----- Set year.
        self.logger.debug("Set year.")
        self._otags["year"] = self._otags["bootlegtrackyear"][:4]

        # ----- Set albumsort.
        self.logger.debug("Set albumsort.")
        self._otags["albumsort"] = "2.{date}.{uid}.{enc}".format(date=self.rex1.sub("", self._otags.get("groupby", self._otags["bootlegtrackyear"])),
                                                                 uid=self._otags["albumsortcount"],
                                                                 enc=self._encoder.code)

        # ----- Set titlesort.
        self.logger.debug("Set titlesort.")
        self._otags["titlesort"] = "D{disc}.T{track}.{bonus}{live}{bootleg}".format(disc=self._otags["disc"],
                                                                                    track=self._otags["track"].zfill(2),
                                                                                    bonus=self._otags["bonus"],
                                                                                    live=self._otags["live"],
                                                                                    bootleg=self._otags["bootleg"])


class SpringsteenBootlegCDTrack(BootlegCDTrack):

    tags = {}
    logger = logging.getLogger("{0}.SpringsteenBootlegCDTrack".format(__name__))

    def __init__(self, **kwargs):
        super(SpringsteenBootlegCDTrack, self).__init__(**kwargs)

        # ----- Check mandatory input tags.
        for item in (item for item in SpringsteenBootlegCDTrack.tags if SpringsteenBootlegCDTrack.tags[item]):
            if item not in kwargs:
                raise ValueError("{0} isn\'t available.".format(item))

        # ----- Update tags.
        self._otags.update({key: kwargs[key] for key in kwargs if key in SpringsteenBootlegCDTrack.tags})

        # ----- Set album.
        self.logger.debug("Set album.")
        self._otags["album"] = "{tour} - {date} - [{city}]".format(tour=self._otags["bootlegtracktour"], date=self.rex1.sub(".", self._otags["bootlegtrackyear"]), city=self._otags["bootlegtrackcity"])

        # ----- Update albumartist.
        self.logger.debug("Update albumartist.")
        self._otags["albumartist"] = "Bruce Springsteen And The E Street Band"

        # ----- Log new tags.
        self.logger.debug("Build tags.")
        self.logger.debug("\talbum    : %s".expandtabs(4) % (self._otags["album"],))
        self.logger.debug("\talbumsort: %s".expandtabs(4) % (self._otags["albumsort"],))
        self.logger.debug("\ttitlesort: %s".expandtabs(4) % (self._otags["titlesort"],))
        self.logger.debug("\tyear     : %s".expandtabs(4) % (self._otags["year"],))


class RippedCD(ContextDecorator):

    environment = Environment(loader=FileSystemLoader(os.path.join(os.path.expandvars("%_PYTHONPROJECT%"), "AudioCD", "RippedCD")), trim_blocks=True, lstrip_blocks=True)
    outputtags = environment.get_template("Tags")
    logger = logging.getLogger("{0}.RippedCD".format(__name__))

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
        self.logger.debug('START "%s".' % (os.path.basename(__file__),))
        self.logger.debug('"{0}" used as ripping profile.'.format(self.profile))

        # --> 2. Log input tags.
        self.logger.debug("Input file.")
        self.logger.debug('\t"{0}"'.format(self.tags).expandtabs(4))
        self.logger.debug("Input tags.")
        if os.path.exists(self.tags):
            with open(self.tags, encoding=shared.UTF16) as fr:
                for line in filcontents(fr):
                    match = re.match(DFTPATTERN, line)
                    if match:
                        self.logger.debug("\t{0}".format("{0}={1}".format(match.group(1), match.group(2))).expandtabs(4))

        # --> 3. Create AudioCDTrack instance.
        self._rippedcd = PROFILES[self.profile].isinstancedfrom(self.tags, shared.UTF16)  # l'attribut "_rippedcd" est une instance de type "AudioCDTrack".

        # --> 4. Store input tags.
        shutil.copy(src=self.tags, dst=os.path.join(os.path.expandvars("%TEMP%"), "iT{0}.txt".format(self._rippedcd.tracknumber.zfill(2))))

        # --> 5. Return instance.
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):

        outtags = {key: self.new[key] for key in self.new if key not in PROFILES[self.profile].exclusions}

        # --> 1. Log output tags.
        self.logger.debug("Output tags.")
        for k, v in outtags.items():
            self.logger.debug("\t{0}={1}".format(k, v).expandtabs(4))

        # --> 2. Store tags.
        self.logger.debug("Store tags.")
        fo, encoding = self.tags, shared.UTF16
        if self.test:
            fo, encoding = os.path.join(os.path.expandvars("%TEMP%"), "oT{0}.txt".format(self.new.tracknumber.zfill(2))), shared.UTF8
        with open(fo, mode=shared.WRITE, encoding=encoding) as fw:
            self.logger.debug("\t{0}".format(fo).expandtabs(4))
            fw.write(self.outputtags.render(tags=outtags))

        # --> 3. Store tags in JSON.
        self.logger.debug("Store tags in single JSON file.")
        tags, obj = os.path.join(os.path.expandvars("%TEMP%"), "tags.json"), []
        if os.path.exists(tags):
            with open(tags, encoding="UTF_8") as fr:
                obj = json.load(fr)
        obj.append(outtags)
        with open(tags, mode=shared.WRITE, encoding="UTF_8") as fw:
            json.dump(obj, fw, indent=4, sort_keys=True)

        # --> 4. Store tags in JSON.
        self.logger.debug("Store tags in per track JSON file.")
        tags = os.path.join(os.path.expandvars("%TEMP%"), "T{0}.json".format(self.new.tracknumber.zfill(2)))
        with open(tags, mode=shared.WRITE, encoding="UTF_8") as fw:
            json.dump(outtags, fw, indent=4, sort_keys=True)

        # --> 5. Stop logging.
        self.logger.debug('END "%s".' % (os.path.basename(__file__),))


class AudioFilesList(MutableSequence):

    logger = logging.getLogger("{0}.AudioFilesList".format(__name__))

    def __init__(self, *extensions, folder, excluded=None):
        self.logger.debug(extensions)
        self.logger.debug(folder)
        self.logger.debug(excluded)
        self._reflist = [(fil,
                          os.path.splitext(fil)[1][1:],
                          tags["artist"],
                          os.path.getctime(fil))
                         for fil, tags in (
                             (fil.file, fil.tags) for fil in map(getmetadata, shared.filesinfolder(*extensions, folder=folder, excluded=excluded)) if fil.found
                         ) if "artist" in tags]

    def __getitem__(self, item):
        return sorted(self._reflist, key=itemgetter(0))[item]

    def __setitem__(self, key, value):
        sorted(self._reflist, key=itemgetter(0))[key] = value

    def __delitem__(self, key):
        del sorted(self._reflist, key=itemgetter(0))[key]

    def __len__(self):
        return len(self._reflist)

    def insert(self, index, value):
        sorted(self._reflist, key=itemgetter(0)).insert(index, value)

    @property
    def reflist(self):
        return self._reflist

    @property
    def sortedby_extension(self):
        reflist = sorted(sorted(self._reflist, key=itemgetter(0)), key=itemgetter(1))
        for item in reflist:
            self.logger.debug(itemgetter(0)(item))
            self.logger.debug(itemgetter(1)(item))
        return reflist

    @property
    def groupedby_extension(self):
        return itertools.groupby(self.sortedby_extension, key=itemgetter(1))

    @property
    def countby_extension(self):
        return [(key, len(list(group))) for key, group in self.groupedby_extension]

    @property
    def sortedby_artist(self):
        reflist = sorted(sorted(self._reflist, key=itemgetter(0)), key=itemgetter(2))
        for item in reflist:
            self.logger.debug(itemgetter(0)(item))
            self.logger.debug(itemgetter(1)(item))
        return reflist

    @property
    def groupedby_artist(self):
        return itertools.groupby(self.sortedby_artist, key=itemgetter(2))

    @property
    def countby_artist(self):
        return [(key, len(list(group))) for key, group in self.groupedby_artist]

    @property
    def sortedby_artist_extension(self):
        reflist = sorted(sorted(sorted(self._reflist, key=itemgetter(0)), key=itemgetter(1)), key=itemgetter(2))
        for item in reflist:
            self.logger.debug(itemgetter(0)(item))
            self.logger.debug(itemgetter(1)(item))
            self.logger.debug(itemgetter(2)(item))
        return reflist

    @property
    def groupedby_artist_extension(self):
        return itertools.groupby(self.sortedby_artist_extension, key=self.keyfunc)

    @property
    def countby_artist_extension(self):
        reflist = [(art, ext, count) for (art, ext), count in ((key, len(list(group))) for key, group in self.groupedby_artist_extension)]
        reflist = sorted(sorted(reflist, key=itemgetter(1)), key=itemgetter(0))
        return itertools.groupby(reflist, key=itemgetter(0))

    @property
    def alternative_countby_artist_extension(self):
        reflist = [(art, ext, count) for (art, ext), count in ((key, len(list(group))) for key, group in self.groupedby_artist_extension)]
        reflist = sorted(sorted(sorted(reflist, key=itemgetter(1)), key=itemgetter(2), reverse=True), key=itemgetter(0))
        return itertools.groupby(reflist, key=itemgetter(0))

    @staticmethod
    def keyfunc(item):
        return itemgetter(2)(item), itemgetter(1)(item)


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
    if fe.lower() in (item.lower() for item in tu):
        return True
    return False


def validdelay(d):
    try:
        delay = int(d)
    except ValueError:
        raise argparse.ArgumentTypeError('"{0}" isn\'t a valid delay.'.format(d))
    if delay > 120:
        return 120
    return delay


def filcontents(fil):
    for line in fil:
        if line.startswith("#"):
            continue
        if not line:
            continue
        yield line


def album(track):
    try:
        totaldiscs = int(track.totaldiscs)
    except ValueError:
        return track.album
    if totaldiscs > 1:
        return "{o.album} ({o.discnumber}/{o.totaldiscs})".format(o=track)
    return track.album


def rippinglog(track, fil=os.path.join(os.path.expandvars("%TEMP%"), "rippinglog.json")):

    obj = []
    if os.path.exists(fil):
        with open(fil, encoding="UTF_8") as fr:
            obj = json.load(fr)
        obj = [tuple(item) for item in obj]
    while True:
        obj.append(
            tuple(
                [
                    track.artist,
                    track.year,
                    album(track),
                    track.genre,
                    track.upc,
                    track.albumsort[:-3],
                    track.artistsort
                ]
            )
        )
        try:
            obj = list(set(obj))
        except TypeError:
            obj.clear()
        else:
            break
    with open(fil, mode=shared.WRITE, encoding="UTF_8") as fw:
        json.dump(sorted(obj, key=itemgetter(0)), fw, indent=4, sort_keys=True)


def digitalaudiobase(track, fil=os.path.join(os.path.expandvars("%TEMP%"), "digitalaudiodatabase.json")):

    obj = []
    if os.path.exists(fil):
        with open(fil, encoding="UTF_8") as fr:
            obj = json.load(fr)
        obj = [tuple(item) for item in obj]
    while True:
        obj.append(
            tuple(
                [
                    track.index,
                    track.albumsort[:-3],
                    track.titlesort,
                    track.artist,
                    track.year,
                    track.album,
                    track.genre,
                    track.discnumber,
                    track.totaldiscs,
                    track.label,
                    track.tracknumber,
                    track.totaltracks,
                    track.title,
                    track.live,
                    track.bootleg,
                    track.incollection,
                    track.upc,
                    track.encodingyear,
                    track.titlelanguage,
                    track.origyear
                ]
            )
        )
        try:
            obj = list(set(obj))
        except TypeError:
            obj.clear()
        else:
            break
    with open(fil, mode=shared.WRITE, encoding="UTF_8") as fw:
        json.dump(sorted(obj, key=itemgetter(0)), fw, indent=4, sort_keys=True)


def getmetadata(audiofil):
    """
    Get metada from an audio file.
    FLAC or Monkey's Audio are only processed.
    :param audiofil: characters string representing an audio file.
    :return: four attributes named tuple:
                - "file". Both dirname and basename of the audio file.
                - "found". Boolean value depending on whether metadata have been found or not.
                - "tags". Dictionary enumerating each metadata found.
                - "object". Audio file object.
    """
    tags, result = {}, namedtuple("result", "file found tags object")
    logger = logging.getLogger("{0}.getmetadata".format(__name__))
    logger.debug(audiofil)

    # Guess "audiofil" type.
    try:
        audioobj = mutagen.File(audiofil, easy=True)
    except (mutagen.MutagenError, TypeError, ZeroDivisionError) as err:
        logger.exception(err)
        return result(audiofil, False, {}, None)

    # Is "audiofil" a valid audio file?
    if not audioobj:
        return result(audiofil, False, {}, None)

    # Is "audiofil" type FLAC, Monkey's Audio or MP3 (with ID3 tags)?
    if any([isinstance(audioobj, mutagen.flac.FLAC), isinstance(audioobj, mutagen.monkeysaudio.MonkeysAudio), isinstance(audioobj, mutagen.mp3.MP3)]):

        # --> FLAC.
        try:
            assert isinstance(audioobj, mutagen.flac.FLAC) is True
        except AssertionError:
            pass
        else:
            tags = dict([(k.lower(), v) for k, v in audioobj.tags])

        # --> Monkey's audio.
        try:
            assert isinstance(audioobj, mutagen.monkeysaudio.MonkeysAudio) is True
        except AssertionError:
            pass
        else:
            tags = {k.lower(): str(v) for k, v in audioobj.tags.items() if isinstance(v, APETextValue)}

        # --> MP3 (with ID3 tags).
        try:
            assert isinstance(audioobj, mutagen.mp3.MP3) is True
        except AssertionError:
            pass
        else:

            # Map user-defined text frame key.
            for key in ["incollection", "titlelanguage", "totaltracks", "totaldiscs", "upc", "encoder"]:
                description, cycle = key, 0
                while True:
                    EasyID3.RegisterTXXXKey(key, description)
                    if key.lower() in (item.lower() for item in audioobj.tags):
                        break
                    cycle += 1
                    if cycle > 1:
                        break
                    description = key.upper()

            # Map normalized text frame key.
            for key, description in [("artistsort", "TSOP"), ("albumartistsort", "TSO2"), ("albumsort", "TSOA"), ("mediatype", "TMED"), ("encodingtime", "TDEN"), ("label", "TPUB")]:
                EasyID3.RegisterTextKey(key, description)

            # Aggregate ID3 frames.
            tags = {k.lower(): v[0] for k, v in audioobj.tags.items()}

    # Have "audiofil" metadata been retrieved?
    if not tags:
        return result(audiofil, False, {}, None)
    return result(audiofil, True, tags, audioobj)


def updatemetadata(audioobj, logger=None, **kwargs):
    """
    Update metadata of an audio file.
    :param audioobj: audio file object.
    :param logger: logger to log raised exception(s).
    :param kwargs: dictionary enumerating metadata to update.
    :return: boolean value depending on whether metadata have been updated or not.
    """
    for k, v in kwargs.items():
        audioobj[k] = v
    try:
        audioobj.save()
    except mutagen.MutagenError as err:
        if logger:
            logger.exception(err)
        return False
    return True


def audiofilesinfolder(*extensions, folder):
    """
    Return a generator object yielding both FLAC and Monkey's Audio files stored in "folder" having extension enumerated in "extensions".
    :param extensions: not mandatory list of extension(s) to filter files.
    :param folder: folder to walk through.
    :return: generator object.
    """
    return ((result.file, result.object, result.tags) for result in map(getmetadata, shared.filesinfolder(*extensions, folder=folder)) if result.found)


def copy_audiofiles_to_remotedirectory(*args, server=shared.NAS, user="admin", password=b85decode(shared.PASSWORD).decode()):
    """
    Upload audio file(s) to a remote directory on the NAS server.
    :param args: list of audio files.
    :param server: IP address of the NAS server.
    :param user: user for creating connection to the server.
    :param password: password for creating connection to the server.
    :return: None.
    """

    # --> Check existing files.
    if not any(map(os.path.exists, args)):
        return

    # --> Logging.
    logger = logging.getLogger("{0}.copy_audiofiles_to_remotedirectory".format(__name__))

    # --> Initializations.
    refdirectory = "/music"
    genexp = ((item.file, item.tags) for item in (getmetadata(file) for file in compress(args, map(os.path.exists, args))) if item.found)
    files = dict([(a, b["albumsort"][:-3]) for a, b in genexp if "albumsort" in b])

    # --> Copy local audio files to remote directory.
    stack1 = ExitStack()
    try:
        ftp = stack1.enter_context(ftputil.FTPHost(server, user, password))
    except ftputil.error.FTPOSError as err:
        logger.exception(err)
    else:
        with stack1:
            ftp.chdir(refdirectory)
            for file in files:
                wdir = ftp.path.join(refdirectory, "/".join(os.path.splitdrive(os.path.dirname(file))[1][1:].split("\\")))
                logger.debug(wdir)
                logger.debug(file)
                logger.debug(files[file])
                stack2 = ExitStack()
                while True:
                    try:
                        stack2.enter_context(shared.AlternativeChangeRemoteCurrentDirectory(ftp, wdir))
                    except ftputil.error.PermanentError:
                        ftp.makedirs(wdir)
                    else:
                        break
                with stack2:
                    ftp.upload(file, os.path.basename(file))
                logger.debug(ftp.getcwd())


# ================
# Initializations.
# ================
profile = namedtuple("profile", "exclusions isinstancedfrom")


# ==========
# Constants.
# ==========
TABSIZE = 3
DFTPATTERN = r"^(?:\ufeff)?(?!#)(?:z_)?([^=]+)=(.+)$"
GENRES = os.path.join(os.path.expandvars("%_PYTHONPROJECT%"), "AudioCD", "Genres.json")
LANGUAGES = os.path.join(os.path.expandvars("%_PYTHONPROJECT%"), "AudioCD", "Languages.json")
ENCODERS = os.path.join(os.path.expandvars("%_PYTHONPROJECT%"), "AudioCD", "Encoders.json")
TITLES = os.path.join(os.path.expandvars("%_COMPUTING%"), "Titles.json")
ENC_KEYS = ["name", "code", "folder", "extension"]
TIT_KEYS = ["number", "title", "overwrite"]
PROFILES = {"default": profile(["albumsortcount", "bootleg", "live", "bonus"], DefaultCDTrack.fromfile),
            "default1": profile(["albumsortcount", "bootleg", "live", "bonus"], DefaultCDTrack.fromfile),
            "selftitled": profile(["albumsortcount", "bootleg", "live", "bonus"], SelfTitledCDTrack.fromfile),
            "sbootlegs": profile(["albumsortcount", "bootleg", "live", "bonus", "groupby"], SpringsteenBootlegCDTrack.fromfile)}
with open(os.path.normpath(os.path.join(os.path.expandvars("%_PYTHONPROJECT%"), "AudioCD", "Mapping.json")), encoding="UTF_8") as fp:
    MAPPING = json.load(fp)
