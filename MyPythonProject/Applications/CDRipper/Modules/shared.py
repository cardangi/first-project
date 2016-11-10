# -*- coding: ISO-8859-1 -*-
from collections import MutableMapping, MutableSequence, namedtuple
from jinja2 import Environment, FileSystemLoader
from sortedcontainers import SortedDict
from contextlib import ContextDecorator
from datetime import datetime
import mutagen.monkeysaudio
from pytz import timezone
import mutagen.flac
import argparse
import mutagen
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
class AudioCDTrack(MutableMapping):

    tags = {"artistsort": True, "albumartistsort": False, "artist": True, "albumartist": False, "encoder": True, "disc": True, "track": True, "title": False, "profile": False, "source": False, "bootleg": True,
            "live": True, "incollection": True, "titlelanguage": False, "genre": False, "style": False, "rating": False, "_albumart_1_front album cover": False}

    def __init__(self, **kwargs):

        nt = namedtuple("nt", "name code folder extension")
        regex = re.compile(r"^(\d{1,2})/(\d{1,2})")
        self._encoder = None
        self._otags = dict()

        # ----- Check mandatory input tags.
        for item in [item for item in AudioCDTrack.tags if AudioCDTrack.tags[item]]:
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
        logger.debug("Set encodedby.")
        self._otags["encodedby"] = "dBpoweramp 15.1 on {0}".format(shared.dateformat(datetime.now(tz=timezone(shared.DFTTIMEZONE)), shared.TEMPLATE3))

        # ----- Set taggingtime.
        logger.debug("Set taggingtime.")
        self._otags["taggingtime"] = shared.dateformat(datetime.now(tz=timezone(shared.DFTTIMEZONE)), shared.TEMPLATE3)

        # ----- Set encodingtime.
        logger.debug("Set encodingtime.")
        self._otags["encodingtime"] = int(datetime.now(tz=timezone(shared.DFTTIMEZONE)).timestamp())

        # ----- Set encodingyear.
        logger.debug("Set encodingyear.")
        self._otags["encodingyear"] = datetime.now(tz=timezone(shared.DFTTIMEZONE)).strftime("%Y")

        # ----- Set encoder attributes.
        logger.debug("Set encoder attributes.")
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
        logger.debug("Set track.")
        self._otags["track"], self._otags[MAPPING.get(kwargs["encoder"], MAPPING["default"])["totaltracks"]] = self.splitfield(kwargs["track"], regex)

        # ----- Both update disc and set total discs.
        logger.debug("Set disc.")
        self._otags["disc"], self._otags[MAPPING.get(kwargs["encoder"], MAPPING["default"])["totaldiscs"]] = self.splitfield(kwargs["disc"], regex)

        # ----- Update genre.
        logger.debug("Update genre.")
        for artist, genre in self.deserialize(GENRES):
            if kwargs["artist"].lower() == artist.lower():
                self._otags["genre"] = genre
                break

        # ----- Update titlelanguage.
        logger.debug("Update titlelanguage.")
        for artist, language in self.deserialize(LANGUAGES):
            if kwargs["artist"].lower() == artist.lower():
                self._otags["titlelanguage"] = language
                break

        # ----- Update title.
        logger.debug("Update title.")
        for track in self.deserialize(TITLES):  # "track" est un dictionnaire.
            if sorted(list(track.keys())) == sorted(TIT_KEYS):
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


class DefaultCDTrack(AudioCDTrack):

    tags = {"origyear": False, "year": True, "albumsortcount": True, "album": True, "upc": True, "label": True, "bonus": False}

    def __init__(self, **kwargs):
        super(DefaultCDTrack, self).__init__(**kwargs)

        # ----- Check mandatory input tags.
        for item in [item for item in DefaultCDTrack.tags if DefaultCDTrack.tags[item]]:
            if item not in kwargs:
                raise ValueError("{0} isn\'t available.".format(item))

        # ----- Update tags.
        self._otags.update({key: kwargs[key] for key in kwargs if key in DefaultCDTrack.tags})

        # ----- Set origyear.
        logger.debug("Set origyear.")
        self._otags["origyear"] = self._otags.get("origyear", self._otags["year"])

        # ----- Set albumsort.
        logger.debug("Set albumsort.")
        self._otags["albumsort"] = "1.{year}0000.{uid}.{enc}".format(year=self._otags["origyear"], uid=self._otags["albumsortcount"], enc=self._encoder.code)

        # ----- Set titlesort.
        logger.debug("Set titlesort.")
        self._otags["titlesort"] = "D{disc}.T{track}.{bonus}{live}{bootleg}".format(disc=self._otags["disc"],
                                                                                    track=self._otags["track"].zfill(2),
                                                                                    bonus=self._otags.get("bonus", "N"),
                                                                                    live=self._otags["live"],
                                                                                    bootleg=self._otags["bootleg"])

        # ----- Update album.
        logger.debug("Update album.")
        self._otags["album"] = self.case(self._otags["album"])

        # ----- Log new tags.
        logger.debug("Build tags.")
        logger.debug("\talbum    : %s".expandtabs(4) % (self._otags["album"],))
        logger.debug("\talbumsort: %s".expandtabs(4) % (self._otags["albumsort"],))
        logger.debug("\ttitlesort: %s".expandtabs(4) % (self._otags["titlesort"],))
        logger.debug("\torigyear : %s".expandtabs(4) % (self._otags["origyear"],))


class SelfTitledCDTrack(DefaultCDTrack):

    tags = {}

    def __init__(self, **kwargs):
        super(SelfTitledCDTrack, self).__init__(**kwargs)

        # ----- Check mandatory input tags.
        for item in [item for item in SelfTitledCDTrack.tags if SelfTitledCDTrack.tags[item]]:
            if item not in kwargs:
                raise ValueError("{0} isn\'t available.".format(item))

        # ----- Update tags.
        self._otags.update({key: kwargs[key] for key in kwargs if key in SelfTitledCDTrack.tags})

        # ----- Update album.
        logger.debug("Update album.")
        self._otags["album"] = "{year} (Self Titled)".format(year=self._otags["origyear"])


# class FiioX5Track(DefaultCDTrack):
#
#     tags = {}
#
#     def __init__(self, **kwargs):
#         super(FiioX5Track, self).__init__(**kwargs)
#
#         # ----- Check mandatory input tags.
#         for item in [item for item in FiioX5Track.tags if FiioX5Track.tags[item]]:
#             if item not in kwargs:
#                 raise ValueError("{0} isn\'t available.".format(item))
#
#         # ----- Update tags.
#         self._otags.update({key: kwargs[key] for key in kwargs if key in FiioX5Track.tags})
#
#         # ----- Update album.
#         logger.debug("Update album.")
#         self._otags["album"] = "{year}.{uid} - {album}".format(year=self._otags["origyear"], uid=self._otags["albumsortcount"], album=self._otags["album"])


class BootlegCDTrack(AudioCDTrack):

    tags = {"bootlegtracktour": True, "bootlegtrackyear": True, "bootlegtrackcity": True, "albumsortcount": True, "provider": False, "providerreference": False, "origalbum": False, "groupby": False, "bonus": True}
    rex1 = re.compile(r"\W+")
    rex2 = re.compile(r", ([A-Z][a-z]+)$")
    DFTCOUNTRY = "United States"

    def __init__(self, **kwargs):
        super(BootlegCDTrack, self).__init__(**kwargs)

        # ----- Check mandatory input tags.
        for item in [item for item in BootlegCDTrack.tags if BootlegCDTrack.tags[item]]:
            if item not in kwargs:
                raise ValueError("{0} isn\'t available.".format(item))

        # ----- Update tags.
        self._otags.update({key: kwargs[key] for key in kwargs if key in BootlegCDTrack.tags})

        # ----- Update bootlegtrackyear.
        logger.debug("Update bootlegtrackyear.")
        self._otags["bootlegtrackyear"] = self.rex1.sub("-", self._otags["bootlegtrackyear"])
        
        # ----- Set bootlegtrackcountry.
        logger.debug("Set bootlegtrackcountry.")
        self._otags["bootlegtrackcountry"] = BootlegCDTrack.DFTCOUNTRY
        match = self.rex2.search(self._otags["bootlegtrackcity"])
        if match:
            self._otags["bootlegtrackcountry"] = match.group(1)

        # ----- Set year.
        logger.debug("Set year.")
        self._otags["year"] = self._otags["bootlegtrackyear"][:4]

        # ----- Set albumsort.
        logger.debug("Set albumsort.")
        self._otags["albumsort"] = "2.{date}.{uid}.{enc}".format(date=self.rex1.sub("", self._otags.get("groupby", self._otags["bootlegtrackyear"])),
                                                                 uid=self._otags["albumsortcount"],
                                                                 enc=self._encoder.code)

        # ----- Set titlesort.
        logger.debug("Set titlesort.")
        self._otags["titlesort"] = "D{disc}.T{track}.{bonus}{live}{bootleg}".format(disc=self._otags["disc"],
                                                                                    track=self._otags["track"].zfill(2),
                                                                                    bonus=self._otags["bonus"],
                                                                                    live=self._otags["live"],
                                                                                    bootleg=self._otags["bootleg"])


class SpringsteenBootlegCDTrack(BootlegCDTrack):

    tags = {}

    def __init__(self, **kwargs):
        super(SpringsteenBootlegCDTrack, self).__init__(**kwargs)

        # ----- Check mandatory input tags.
        for item in [item for item in SpringsteenBootlegCDTrack.tags if SpringsteenBootlegCDTrack.tags[item]]:
            if item not in kwargs:
                raise ValueError("{0} isn\'t available.".format(item))

        # ----- Update tags.
        self._otags.update({key: kwargs[key] for key in kwargs if key in SpringsteenBootlegCDTrack.tags})

        # ----- Set album.
        logger.debug("Set album.")
        self._otags["album"] = "{tour} - {date} - [{city}]".format(tour=self._otags["bootlegtracktour"], date=self.rex1.sub(".", self._otags["bootlegtrackyear"]), city=self._otags["bootlegtrackcity"])

        # ----- Update albumartist.
        logger.debug("Update albumartist.")
        self._otags["albumartist"] = "Bruce Springsteen And The E Street Band"

        # ----- Log new tags.
        logger.debug("Build tags.")
        logger.debug("\talbum    : %s".expandtabs(4) % (self._otags["album"],))
        logger.debug("\talbumsort: %s".expandtabs(4) % (self._otags["albumsort"],))
        logger.debug("\ttitlesort: %s".expandtabs(4) % (self._otags["titlesort"],))
        logger.debug("\tyear     : %s".expandtabs(4) % (self._otags["year"],))


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

        # --> 3. Create AudioCDTrack instance.
        self._rippedcd = PROFILES[self.profile].isinstancedfrom(self.tags, shared.UTF16)  # l'attribut "_rippedcd" est une instance de type "AudioCDTrack".

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


class AudioFilesCollection(MutableSequence):

    rex1 = re.compile(r"^(?:{0})\.\d \-\B".format(shared.DFTYEARREGEX))
    tags = ["albumsort", "album"]

    def __init__(self, path):
        self._seq = []

    def __getitem__(self, item):
        return self._seq[item]

    def __setitem__(self, key, value):
        self._seq[key] = value

    def __delitem__(self, key):
        del self._seq[key]

    def __len__(self):
        return len(self._seq)

    def __call__(self, *psargs, **kwargs):
        l = []
        for num, fil, tags in [(a, b, c) for a, (b, c) in enumerate(self, 1)]:
            album = "{0}.{1} - {2}".format(tags["albumsort"][2:6], tags["albumsort"][-1:], tags["album"])
            logger.debug('{0:>3d}. "{1}".'.format(num, fil))
            logger.debug('\tNew album: "{0}".'.format(album).expandtabs(TABSIZE))
            if not kwargs["test"]:
                try:
                    tags["album"] = album
                    tags.save()
                except mutagen.MutagenError as err:
                    logger.debug(err)
                else:
                    l.append(fil)
        if l:
            logger.debug("{0:>5d} files updated.".format(len(l)))

    def insert(self, index, value):
        self._seq.insert(index, value)


class FLACFilesCollection(AudioFilesCollection):

    rex2 = re.compile(r"^(?=1\.\d[\d\.]+$)(?=[\d\.]+\.13$)1\.(?:{0})0000\.\d\.13$".format(shared.DFTYEARREGEX))

    def __init__(self, path):
        super(FLACFilesCollection, self).__init__(path)

        for fil in shared.filesinfolder(folder=path):
            try:
                audio = mutagen.flac.FLAC(fil)
            except mutagen.MutagenError:
                continue

            # Contrôler que les tags obligatoires sont présents.
            if any([tag not in audio for tag in self.tags]):
                continue

            # Ne retenir que les fichiers dont le tag "albumsort" est cohérent.
            match = self.rex2.match(audio["albumsort"])
            if not match:
                continue

            # Ne retenir que les fichiers dont le tag "album" n'a pas été déjà modifié.
            match = self.rex1.match(audio["album"])
            if match:
                continue

            # Retenir le fichier.
            self._seq.append((fil, audio))


class MonkeyFilesCollection(AudioFilesCollection):

    rex2 = re.compile(r"^(?=1\.\d[\d\.]+$)(?=[\d\.]+\.15$)1\.(?:{0})0000\.\d\.15$".format(shared.DFTYEARREGEX))

    def __init__(self, path):
        super(MonkeyFilesCollection, self).__init__(path)

        for fil in shared.filesinfolder(folder=path):
            try:
                audio = mutagen.monkeysaudio.MonkeysAudio(fil)
            except mutagen.MutagenError:
                continue

            # Contrôler que les tags obligatoires sont présents.
            if any([tag not in audio for tag in self.tags]):
                continue

            # Ne retenir que les fichiers dont le tag "albumsort" est cohérent.
            match = self.rex2.match(audio["albumsort"])
            if not match:
                continue

            # Ne retenir que les fichiers dont le tag "album" n'a pas été déjà modifié.
            match = self.rex1.match(audio["album"])
            if match:
                continue

            # Retenir le fichier.
            self._seq.append((fil, audio))


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


def validdelay(d):
    try:
        delay = int(d)
    except ValueError:
        raise argparse.ArgumentTypeError('"{0}" isn\'t a valid delay.'.format(d))
    if delay > 60:
        return 60
    return delay


# ================
# Initializations.
# ================
profile = namedtuple("profile", "exclusions isinstancedfrom")


# ==========
# Constants.
# ==========
TABSIZE = 3
DFTPATTERN = r"^(?:\ufeff)?(?!#)(?:z_)?([^=]+)=(.+)$"
GENRES = os.path.join(os.path.expandvars("%_PYTHONPROJECT%"), "Applications", "CDRipper", "Genres.json")
LANGUAGES = os.path.join(os.path.expandvars("%_PYTHONPROJECT%"), "Applications", "CDRipper", "Languages.json")
ENCODERS = os.path.join(os.path.expandvars("%_PYTHONPROJECT%"), "Applications", "CDRipper", "Encoders.json")
TITLES = os.path.join(os.path.expandvars("%_COMPUTING%"), "Titles.json")
ENC_KEYS = ["name", "code", "folder", "extension"]
TIT_KEYS = ["number", "title", "overwrite"]
PROFILES = {"default": profile(["albumsortcount", "bootleg", "live", "bonus"], DefaultCDTrack.fromfile),
            "default1": profile(["albumsortcount", "bootleg", "live", "bonus"], DefaultCDTrack.fromfile),
            "selftitled": profile(["albumsortcount", "bootleg", "live", "bonus"], SelfTitledCDTrack.fromfile),
            "sbootlegs": profile(["albumsortcount", "bootleg", "live", "bonus", "groupby"], SpringsteenBootlegCDTrack.fromfile)}
with open(os.path.join(os.path.expandvars("%_PYTHONPROJECT%"), r"Applications/CDRipper/Mapping.json")) as fp:
    MAPPING = json.load(fp)
