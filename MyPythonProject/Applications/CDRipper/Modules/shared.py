# -*- coding: ISO-8859-1 -*-
__author__ = 'Xavier ROSSET'


# =================
# Absolute imports.
# =================
from sortedcontainers import SortedDict
from datetime import datetime
from pytz import timezone
import re


# =================
# Relative imports.
# =================
from ... import shared
from ...Database.Modules import shared as s2


# ==========
# Constants.
# ==========
DFTPATTERN = r"^(?:\ufeff)?(?!#)(?:z_)?([^=]+)=(.+)$"
PROFILES = ["default", "defaultbootlegs", "pjbootlegs", "selftitled"]
# PROFILES = ["default", "soundtrack", "sbootlegs", "pjbootlegs", "selftitled", "xbootlegs", "ccbootlegs"]


# ========
# Classes.
# ========
class AudioCD:
    itags = ["artist", "title", "track", "disc", "upc", "profile", "source", "incollection", "titlelanguage", "genre", "artistsort", "albumartist", "albumartistsort", "_albumart_1_front album cover", "style",
             "encoder"]
    otags = ["artist", "title", "track", "disc", "upc", "profile", "source", "incollection", "titlelanguage", "genre", "artistsort", "albumartist", "albumartistsort", "_albumart_1_front album cover", "style",
             "encodedby", "taggingtime", "encodingtime"]

    def __getitem__(self, itm):
        return self.tags[itm]

    def __init__(self, **kwargs):

        self.tags = {}

        # ----- Attributes taken from the input file.
        for i in AudioCD.itags:
            if i in kwargs:
                setattr(self, i, kwargs[i])

        # ----- Attributes initialized with "N".
        for i in ["bonus"]:
            setattr(self, i, "N")

        # ----- Encodedby.
        self.encodedby = "dBpoweramp 15.1 on {}".format(shared.dateformat(datetime.now(tz=timezone(shared.DFTTIMEZONE)), shared.TEMPLATE3))

        # ----- Taggingtime.
        self.taggingtime = shared.dateformat(datetime.now(tz=timezone(shared.DFTTIMEZONE)), shared.TEMPLATE3)

        # ----- Encodingtime.
        self.encodingtime = int(datetime.now(tz=timezone(shared.DFTTIMEZONE)).timestamp())
        self.encodingyear = datetime.now(tz=timezone(shared.DFTTIMEZONE)).strftime("%Y")

        # ----- Encoder attributes.
        if not missingattribute(self, "encoder"):
            encoder = s2.Record(self.encoder, table=s2.Table(table="encoders"))
            if encoder.exists:
                definitions = encoder["definitions"].decode(shared.DFTENCODING).split(";")
                if definitions:
                    self.encodercode = definitions[0]
                    self.encoderfold = definitions[1]
                    self.encoderexte = definitions[2]

        # ----- Tracknumber / Totaltracks.
        if not missingattribute(self, "track"):
            rtn = self.splitfield(self.track, r"^(\d{1,2})/(\d{1,2})")
            if rtn:
                self.tracknumber = rtn[0]
                self.totaltracks = rtn[1]

        # ----- Discnumber / Totaldiscs.
        if not missingattribute(self, "disc"):
            rtn = self.splitfield(self.disc, r"^(\d{1,2})/(\d{1,2})")
            if rtn:
                self.discnumber = rtn[0]
                self.totaldiscs = rtn[1]

        # ----- Genre.
        if not missingattribute(self, "artist"):
            artist = s2.Record(self.artist, table=s2.Table(table="genres"))
            if artist.exists:
                self.genre = artist["genre"]

        # ----- Titlelanguage.
        if not missingattribute(self, "artist"):
            artist = s2.Record(self.artist, table=s2.Table(table="languages"))
            if artist.exists:
                self.genre = artist["language"]

        # ----- Title.
        regex = re.compile(r"^([^=]+)=(.+)$", re.IGNORECASE)
        with open(r"G:\Computing\dBpoweramp - Titles.xav", encoding=shared.DFTENCODING) as f:
            for line in self.contents(f):
                    match = regex.match(line)
                    if match:
                        if match.group(1) == self.track:
                            self.title = match.group(2)
                            break

    def __iter__(self):
        for k, v in self.tags.items():
            yield k, v

    def __len__(self):
        return len(self.tags)

    def __repr__(self):
        return repr(self.tags)

    def get(self, itm):
        return self.tags.get(itm, None)

    def keys(self):
        return list(self.tags.keys())

    def outputtags(self):
        for i in AudioCD.otags:
            if hasattr(self, i):
                self.tags[i] = getattr(self, i)

    @classmethod
    def fromfile(cls, fil, enc=shared.UTF8):
        regex, d = re.compile(r"^(?:\ufeff)?(?!#)(?:z_)?([^=]+)=(.+)$", re.IGNORECASE), {}
        with open(fil, encoding=enc) as f:
            for line in cls.contents(f):
                match = regex.match(line)
                if match:
                    d[match.group(1).rstrip().lower()] = match.group(2)
        return cls(**SortedDict(d))

    @classmethod
    def case(cls, s):
        regex = {1: r"(for|and|nor|but|or|yet|so)",
                 2: r"((?:al)?though|as|because|if|since|so that|such as|to|unless|until|when|where(?:as)?|while)",
                 3: r"(above|after|against|along(?:side)?|around|at|before|behind|below|between|beside|close to|down|(?:far )?from|in(?: front of)?(?:side)?(to)?|near|off?|on(?:to)?|out(?:side)?|over|toward|under"
                    r"(?:neath)?|up(?: to)?)",
                 4: r"(a(?:n(?:d)?)?|as|by|than|the|till|upon)",
                 5: r"[\.\-]+"}

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
        s = re.compile(r"(?i)\b{}\b".format(regex[1])).sub(cls.low, s)
        s = re.compile(r"(?i)\b{}\b".format(regex[2])).sub(cls.low, s)
        s = re.compile(r"(?i)\b{}\b".format(regex[3])).sub(cls.low, s)
        s = re.compile(r"(?i)\b{}\b".format(regex[4])).sub(cls.low, s)

        # -------------------------------------
        # Le début du titre demeure capitalisé.
        # -------------------------------------
        s = re.compile(r"(?i)^{}\b".format(regex[1])).sub(cls.cap1, s)
        s = re.compile(r"(?i)^{}\b".format(regex[2])).sub(cls.cap1, s)
        s = re.compile(r"(?i)^{}\b".format(regex[3])).sub(cls.cap1, s)
        s = re.compile(r"(?i)^{}\b".format(regex[4])).sub(cls.cap1, s)
        s = re.compile(r"(?i)^({})({})\b".format(regex[5], regex[1])).sub(cls.cap2, s)
        s = re.compile(r"(?i)^({})({})\b".format(regex[5], regex[2])).sub(cls.cap2, s)
        s = re.compile(r"(?i)^({})({})\b".format(regex[5], regex[3])).sub(cls.cap2, s)
        s = re.compile(r"(?i)^({})({})\b".format(regex[5], regex[4])).sub(cls.cap2, s)

        # ------------------------------------
        # Les acronymes demeurent capitalisés.
        # ------------------------------------
        s = re.compile(r"(?i)\b(u\.?s\.?a\.?)").sub(cls.upp, s)
        s = re.compile(r"(?i)\b(u\.?k\.?)").sub(cls.upp, s)
        s = re.compile(r"(?i)\b(dj)\b").sub(cls.upp, s)

        # ----------------------------------
        # Autres mots demeurant capitalisés.
        # ----------------------------------
        s = re.compile(r"(?i)\b({})({})\b".format(regex[5], regex[3])).sub(cls.cap2, s)

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
    def isbonustitle(tit):
        """
        Check if title is a bonus title.
        :param tit: title
        :return: tuple composed of (boolean, returned title).
        """
        m = re.compile(r"(?i)^([^\[\(]+)(?:\[|\()bonus(?:\]|\))$").match(tit)
        if m:
            return True, tit[m.start(1):m.end(1)].strip()
        return False, tit

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
        return "{}{}".format(s.groups()[0], s.groups()[1].capitalize())

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
        return "{0}({1})".format(s.groups()[0], s.groups()[1])


class DefaultCD(AudioCD):
    itags = ["label", "year", "album", "origyear", "albumsortcount", "bootleg", "live"]
    otags = ["label", "year", "album", "origyear", "albumsort", "titlesort"]

    def __init__(self, **kwargs):

        super(DefaultCD, self).__init__(**kwargs)
        for i in DefaultCD.itags:
            if i in kwargs:
                setattr(self, i, kwargs[i])

        # ----- Album.
        if not missingattribute(self, *("album",)):
            self.album = self.case(self.album)

        # ----- Albumsort.
        if not missingattribute(self, *("year",)):
            self.albumsortyear = self.year
        if not missingattribute(self, *("origyear",)):
            self.albumsortyear = self.origyear
        if not missingattribute(self, *("albumsortyear", "albumsortcount", "encodercode")):
            self.albumsort = "1.{year}0000.{count}.{enc}".format(year=self.albumsortyear, count=self.albumsortcount, enc=self.encodercode)

        # ----- Titlesort.
        if not missingattribute(self, *("discnumber", "tracknumber", "bonus", "live", "bootleg")):
            self.titlesort = "D{disc}.T{track}.{bonus}{live}{bootleg}".format(disc=self.discnumber, track=self.tracknumber.zfill(2), bonus=self.bonus, live=self.live, bootleg=self.bootleg)

        # ----- Append tags to dictionary.
        self.outputtags()

    def outputtags(self):
        super(DefaultCD, self).outputtags()
        for i in DefaultCD.otags:
            if hasattr(self, i):
                self.tags[i] = getattr(self, i)


# class SoundtrackCD(DefaultCD):
#     itags = []
#     otags = []
#
#     def __init__(self, **kwargs):
#         super(SoundtrackCD, self).__init__(**kwargs)
#         for i in SoundtrackCD.itags:
#             if i in kwargs:
#                 setattr(self, i, kwargs[i])
#         self.outputtags()
#
#     def outputtags(self):
#         super(SoundtrackCD, self).outputtags()
#         for i in SoundtrackCD.otags:
#             if hasattr(self, i):
#                 self.tags[i] = getattr(self, i)


class SelfTitledCD(DefaultCD):
    itags = []
    otags = []

    def __init__(self, **kwargs):
        super(SelfTitledCD, self).__init__(**kwargs)
        for i in SelfTitledCD.itags:
            if i in kwargs:
                setattr(self, i, kwargs[i])
        if not missingattribute(self, *("year",)):
            self.album = "{0} (Self Titled)".format(self.year)
        self.outputtags()

    def outputtags(self):
        super(SelfTitledCD, self).outputtags()
        for i in SelfTitledCD.otags:
            if hasattr(self, i):
                self.tags[i] = getattr(self, i)


class LiveCD(AudioCD):
    itags = []
    otags = []

    def __init__(self, **kwargs):
        super(LiveCD, self).__init__(**kwargs)
        for i in LiveCD.itags:
            if i in kwargs:
                setattr(self, i, kwargs[i])
        self.outputtags()

    def outputtags(self):
        super(LiveCD, self).outputtags()
        for i in LiveCD.otags:
            if hasattr(self, i):
                self.tags[i] = getattr(self, i)

    # @staticmethod
    # def getdate(s, r):
    #     """
    #     Get date from a string by using a regular expression.
    #     :param s: string.
    #     :param r: regular expression.
    #     :return: tuple composed of (boolean, CCYY, MM, DD)
    #     """
    #     m = re.compile(r).match(s)
    #     if m:
    #         return True, m.group(1), m.group(2), m.group(3)
    #     return False, None, None, None

    # @staticmethod
    # def hascomma(s):
    #     """
    #     Check if a string has a comma.
    #     :param s: string.
    #     :return: boolean.
    #     """
    #     return not re.compile(r"^((?!,).)*$").search(s)


class Bootlegs(LiveCD):
    itags = ["bootlegtrackcity", "bootlegtracktour", "bootlegtrackdate"]
    otags = ["bootlegtrackcity", "bootlegtracktour", "bootlegtrackyear", "bootlegtrackcountry"]
    regex1 = re.compile(r"^[^,]+, [A-Z]{2}$")
    regex2 = re.compile(r"^([^,]+), ([a-z]{3,})$", re.IGNORECASE)
    regex3 = re.compile(r"^\b(?:20[012]|19[7-9]\d) \b(?:{0})\b \b(?:{1})\b$".format(shared.DFTMONTHREGEX, shared.DFTDAYREGEX))

    def __init__(self, **kwargs):

        # ----- Attributes taken from the input file.
        super(Bootlegs, self).__init__(**kwargs)
        for i in Bootlegs.itags:
            if i in kwargs:
                setattr(self, i, kwargs[i])

        # Backup bootlegtrackcity.
        self.city = self.bootlegtrackcity

        # ----- Bootlegtrackyear.
        if not missingattribute(self, *("bootlegtrackdate",)):
            if Bootlegs.regex3.match(self.bootlegtrackdate):
                self.bootlegtrackyear = self.bootlegtrackdate.replace(" ", "-")

        # ----- Bootlegtrackcountry.
        if not missingattribute(self, *("bootlegtrackcity",)):
            self.bootlegtrackcountry = "United States"
            if not Bootlegs.regex1.match(self.bootlegtrackcity):
                match = Bootlegs.regex2.match(self.bootlegtrackcity)
                if match:
                    self.bootlegtrackcountry = match.group(2)

        # ----- Bootlegtrackcity.
        if not missingattribute(self, *("bootlegtrackcity",)):
            if not Bootlegs.regex1.match(self.bootlegtrackcity):
                match = Bootlegs.regex2.match(self.bootlegtrackcity)
                if match:
                    self.bootlegtrackcity = match.group(1)

        # ----- Append tags to dictionary.
        self.outputtags()

    def outputtags(self):
        super(Bootlegs, self).outputtags()
        for i in Bootlegs.otags:
            if hasattr(self, i):
                self.tags[i] = getattr(self, i)


class DefaultBootlegs(Bootlegs):
    itags = ["album", "label", "origalbum", "reference", "bootleg", "live"]
    otags = ["album", "label", "origalbum", "publisherreference", "albumsort", "titlesort", "year"]
    regex1 = re.compile(r"^[^\-]+\- \b(20[012]|19[7-9]\d)\.\b({0})\b\.\b({1})\b \- \B.+$".format(shared.DFTMONTHREGEX, shared.DFTDAYREGEX))
    regex2 = re.compile(r"^\b(?:20[012]|19[7-9]\d) \b(?:{0})\b \b(?:{1})\b$".format(shared.DFTMONTHREGEX, shared.DFTDAYREGEX))

    def __init__(self, **kwargs):

        # ----- Attributes taken from the input file.
        super(DefaultBootlegs, self).__init__(**kwargs)
        for i in DefaultBootlegs.itags:
            if i in kwargs:
                setattr(self, i, kwargs[i])

        # ----- Year, Month, Day.
        if not missingattribute(self, *("album",)):
            match = DefaultBootlegs.regex1.match(self.album)
            if match:
                self.year = match.group(1)
                self.month = match.group(2)
                self.day = match.group(3)

        # ----- Albumsort.
        if not missingattribute(self, *("encodercode", "year", "month", "day")):
            self.albumsort = "2.{ccyy}{mm}{dd}.1.{enc}".format(ccyy=self.year, mm=self.month, dd=self.day, enc=self.encodercode)

        # ----- Titlesort.
        self.bonus = "N"
        if not missingattribute(self, *("album", "bootlegtracktour", "bootlegtrackdate", "city")):
            if DefaultBootlegs.regex2.match(self.bootlegtrackdate):
                if self.album != "{0} - {1}.{2}.{3} - [{4}]".format(self.bootlegtracktour, self.bootlegtrackdate[:4], self.bootlegtrackdate[5:7], self.bootlegtrackdate[8:10], self.city):
                    self.bonus = "Y"
        if not missingattribute(self, *("discnumber", "tracknumber", "bonus", "live", "bootleg")):
            self.titlesort = "D{disc}.T{track}.{bonus}{live}{bootleg}".format(disc=self.discnumber, track=self.tracknumber.zfill(2), bonus=self.bonus, live=self.live, bootleg=self.bootleg)

        # ----- Publisherreference.
        if not missingattribute(self, *("reference",)):
            self.publisherreference = self.reference

        # ----- Append tags to dictionary.
        self.outputtags()

    def outputtags(self):
        super(DefaultBootlegs, self).outputtags()
        for i in DefaultBootlegs.otags:
            if hasattr(self, i):
                self.tags[i] = getattr(self, i)


# class CCBootlegs(DefaultBootlegs):
#
#     def __init__(self, **kwargs):
#         super(CCBootlegs, self).__init__(**kwargs)
#         for i in CCBootlegs.itags:
#             if i in kwargs:
#                 setattr(self, i, kwargs[i])
#         self.outputtags()
#
#     def outputtags(self):
#         super(CCBootlegs, self).outputtags()
#         for i in CCBootlegs.otags:
#             if hasattr(self, i):
#                 self.tags[i] = getattr(self, i)


# class SBootlegs(DefaultBootlegs):
#
#     def __init__(self, **kwargs):
#         super(SBootlegs, self).__init__(**kwargs)
#         for i in SBootlegs.itags:
#             if i in kwargs:
#                 setattr(self, i, kwargs[i])
#         self.outputtags()
#
#     def outputtags(self):
#         super(SBootlegs, self).outputtags()
#         for i in SBootlegs.otags:
#             if hasattr(self, i):
#                 self.tags[i] = getattr(self, i)


# class XBootlegs(DefaultBootlegs):
#
#     def __init__(self, **kwargs):
#         super(XBootlegs, self).__init__(**kwargs)
#         for i in XBootlegs.itags:
#             if i in kwargs:
#                 setattr(self, i, kwargs[i])
#         self.outputtags()
#
#     def outputtags(self):
#         super(XBootlegs, self).outputtags()
#         for i in XBootlegs.otags:
#             if hasattr(self, i):
#                 self.tags[i] = getattr(self, i)


class PJBootlegs(Bootlegs):
    itags = ["bootleg", "live"]
    otags = ["album", "albumsort", "titlesort", "year"]
    regex = re.compile(r"^\b(?:20[012]|19[7-9]\d) \b(?:{0})\b \b(?:{1})\b$".format(shared.DFTMONTHREGEX, shared.DFTDAYREGEX))

    def __init__(self, **kwargs):

        # ----- Attributes taken from the input file.
        super(PJBootlegs, self).__init__(**kwargs)
        for i in PJBootlegs.itags:
            if i in kwargs:
                setattr(self, i, kwargs[i])

        # ----- Album.
        if not missingattribute(self, "city", "bootlegtrackdate"):
            if PJBootlegs.regex.match(self.bootlegtrackdate):
                self.album = "Live: {0}-{1}-{2} - {3}".format(self.bootlegtrackdate[:4], self.bootlegtrackdate[5:7], self.bootlegtrackdate[8:10], self.city)

        # ----- Albumsort.
        if not missingattribute(self, "encodercode", "bootlegtrackdate"):
            if PJBootlegs.regex.match(self.bootlegtrackdate):
                self.albumsort = "2.{0}{1}{2}.1.{3}".format(self.bootlegtrackdate[:4], self.bootlegtrackdate[5:7], self.bootlegtrackdate[8:10], self.encodercode)

        # ----- Titlesort.
        if not missingattribute(self, "discnumber", "tracknumber", "live", "bootleg"):
            self.titlesort = "D{disc}.T{track}.N{live}{bootleg}".format(disc=self.discnumber, track=self.tracknumber.zfill(2), live=self.live, bootleg=self.bootleg)

        # ----- Year.
        if not missingattribute(self, "bootlegtrackdate"):
            if PJBootlegs.regex.match(self.bootlegtrackdate):
                self.year = self.bootlegtrackdate[:4]

        # ----- Append tags to dictionary.
        self.outputtags()

    def outputtags(self):
        super(PJBootlegs, self).outputtags()
        for i in PJBootlegs.otags:
            if hasattr(self, i):
                self.tags[i] = getattr(self, i)


# ==========
# Functions.
# ==========
def missingattribute(object, *names):
    """
    Check if an object has got attribute(s).
    :param object: object created from AudioCD class.
    :param names: attribute(s) looked for.
    :return: True: at lease one attribute is missing.
             False: all attributes looked for are present.
    """
    if all(hasattr(object, name) for name in names):
        return False
    return True
