# -*- coding: ISO-8859-1 -*-
import io
import os
import re
import locale
import logging
import argparse
import itertools
from pytz import timezone
from mutagen.mp3 import MP3
from string import Template
from datetime import datetime
from mutagen.flac import FLAC
from dateutil.tz import gettz
from operator import itemgetter
from mutagen import MutagenError
from collections import Iterable
from dateutil.parser import parse
from contextlib import contextmanager
from PIL import Image, TiffImagePlugin
from collections import namedtuple, deque

__author__ = 'Xavier'


# ==========================
# Define French environment.
# ==========================
locale.setlocale(locale.LC_ALL, "")


# ==========
# Constants.
# ==========
APPEND = "a"
WRITE = "w"
DATABASE = r"g:\computing\database.db"
LOG = r"g:\computing\log.log"
DFTENCODING = "ISO-8859-1"
DFTTIMEZONE = "Europe/Paris"
UTC = timezone("UTC")
LOCAL = timezone("Europe/Paris")
TEMPLATE1 = "$day $d/$m/$Y $H:$M:$S $Z$z"
TEMPLATE2 = "$day $d $month $Y $H:$M:$S $Z$z"
TEMPLATE3 = "$d/$m/$Y $H:$M:$S $Z$z"
TEMPLATE4 = "$day $d $month $Y $H:$M:$S ($Z$z)"
TEMPLATE5 = "$Y-$m-$d"
LOGPATTERN = "%(asctime)s [%(name)s]: %(message)s"
UTF8 = "UTF_8"
UTF16 = "UTF_16LE"
UTF16BOM = "\ufeff"
COPYRIGHT = "\u00a9"
DFTYEARREGEX = "20[0-2]\d"
DFTMONTHREGEX = "0[1-9]|1[0-2]"
DFTDAYREGEX = "0[1-9]|[12]\d|3[01]"
ACCEPTEDANSWERS = ["N", "Y"]
ARECA = r'"C:\Program Files\Areca\areca_cl.exe"'
MUSIC = "F:\\"
EXIT = 11
BACK = 12


# ========
# Classes.
# ========
class ImageError(OSError):
    def __init__(self, file, error):
        self.file = file
        self.error = error


class ExifError(ImageError):
    def __init__(self, file, error):
        super(ExifError, self).__init__(file, error)


class Files(object):

    def __contains__(self, itm):
        return itm in self.metadata

    def __getitem__(self, itm):
        return self.metadata[itm]

    def __init__(self, fil):
        self._fil = None
        self.fil = fil
        self._metadata = {i: getattr(self, i) for i in ["ctime", "mtime", "dirname", "basename", "extension", "parts"]}

    @property
    def fil(self):
        return self._fil

    @fil.setter
    def fil(self, value):
        if not os.path.exists(value):
            raise FileNotFoundError('Can\'t find "{0}". Please check both dirname and basename.'.format(value))
        self._fil = value

    @property
    def dirname(self):
        return os.path.dirname(self.fil)

    @property
    def basename(self):
        return os.path.splitext(os.path.basename(self.fil))[0]

    @property
    def extension(self):
        return os.path.splitext(self.fil)[1].strip(".")

    @property
    def parts(self):
        return os.path.dirname(self.fil).split("\\")

    @property
    def ctime(self):
        return int(os.path.getctime(self.fil))

    @property
    def mtime(self):
        return int(os.path.getmtime(self.fil))

    @property
    def metadata(self):
        return self._metadata

    def __iter__(self):
        for k, v in self.metadata.items():
            yield k, v

    def __len__(self):
        return len(self.metadata)

    def __repr__(self):
        return repr(self.metadata)


class Images(Files):

    tzinfos = {"CEST": gettz("Europe/Paris"), "CET": gettz("Europe/Paris")}

    def __init__(self, img):
        super(Images, self).__init__(img)
        self._exif = None
        self.exif = img
        for i in ["localtimestamp", "originaldatetime", "originalyear", "originalmonth", "originalday", "originalhours", "originalminutes", "originalseconds", "dayoftheyear", "dayoftheweek", "defaultlocation",
                  "defaultprefix", "originalsubseconds"]:
            self._metadata[i] = getattr(self, i)

    @property
    def exif(self):
        return self._exif

    @exif.setter
    def exif(self, value):
        try:
            self._exif = self.getexif(Image.open(value))
        except ExifError:
            raise ExifError(value, "Can\'t grab exif tags from")
        except OSError:
            raise OSError('Can\'t identify "{0}" as an image file.'.format(value))
        else:
            if not self._exif:
                raise ExifError(value, "Can\'t grab metadata from")
            if 36867 not in self._exif:
                raise ExifError(value, "Can\'t grab timestamp from")

    @property
    def datetime(self):
        return parse("{0} CET".format(self.exif[36867].replace(":", "-", 2)), tzinfos=self.tzinfos)

    @property
    def localtimestamp(self):
        return int(self.datetime.timestamp())

    @property
    def originaldatetime(self):
        return self.datetime.strftime("%d/%m/%Y %H:%M:%S %Z%z")

    @property
    def originalyear(self):
        return self.datetime.strftime("%Y")

    @property
    def originalmonth(self):
        return self.datetime.strftime("%m")

    @property
    def originalday(self):
        return self.datetime.strftime("%d")

    @property
    def originalhours(self):
        return self.datetime.strftime("%H")

    @property
    def originalminutes(self):
        return self.datetime.strftime("%M")

    @property
    def originalseconds(self):
        return self.datetime.strftime("%S")

    @property
    def originalsubseconds(self):
        return self.exif.get(37521, 0)

    @property
    def dayoftheyear(self):
        return self.datetime.strftime("%j")

    @property
    def dayoftheweek(self):
        return self.datetime.strftime("%w")

    @property
    def defaultlocation(self):
        return self.defaultlocation(self.originalyear, self.originalmonth, self.originalday)

    @property
    def defaultprefix(self):
        return "{0}{1}".format(self.originalyear, str(self.originalmonth).zfill(2))

    @property
    def make(self):
        return self.exif.get(271, "")

    @property
    def model(self):
        return self.exif.get(272, "")

    @property
    def width(self):
        return self.exif.get(40962, 0)

    @property
    def height(self):
        return self.exif.get(40963, 0)

    @property
    def copyright(self):
        return self.exif.get(33432, "")

    @classmethod
    def getexif(cls, o):
        """
        :param o: image object.
        :return: metadata dictionary
        """
        d = {}
        try:
            data = o.info["exif"]
        except KeyError:
            raise ExifError
        file = io.BytesIO(data[6:])
        head = file.read(8)
        info = TiffImagePlugin.ImageFileDirectory(head)
        info.load(file)
        for key, value in info.items():
            d[key] = cls.fixup(value)
        try:
            file.seek(d[0x8769])
        except KeyError:
            pass
        else:
            info = TiffImagePlugin.ImageFileDirectory(head)
            info.load(file)
            for key, value in info.items():
                d[key] = cls.fixup(value)
        return d

    @staticmethod
    def fixup(v):
        if len(v) == 1:
            return v[0]
        return v

    @staticmethod
    def defaultlocation(year, month, day):

        defaultdrive = MUSIC

        # Cas 1 : "h:\CCYY\MM\DD".
        if year in [2011, 2012]:
            return os.path.join(defaultdrive, str(year), str(month).zfill(2), str(day).zfill(2))

        # Cas 2 : "h:\CCYY\MM.DD".
        elif year == 2014:
            return os.path.join(defaultdrive, str(year), "{0}.{1}".format(str(month).zfill(2), str(day).zfill(2)))

        # Cas 3 : "h:\CCYYMM".
        return os.path.join(defaultdrive, "{0}{1}".format(year, str(month).zfill(2)))


class Header(object):

    def __init__(self, header, steps, step=1):
        self._header = header
        self._steps = steps
        self._step = step
        self._index = 0

    def __call__(self):
        self._index += 1
        self._step += 1
        return self._header, self._step - 1, self._steps[self._index - 1]


class Track(object):

    rex = r"^(?:[^{sep}]+{sep}){{{fields}}}[^{sep}]+$"

    def __getitem__(self, index):
        return self._data.split(self._sep)[index]

    def __init__(self, line, fields=2, sep=";"):
        self._sep = sep
        self._data = line
        self._fields = fields
        self._index = 0

    def __iter__(self):
        return self

    def __next__(self):
        if self._index == len(self._data.split(self._sep)):
            raise StopIteration
        self._index += 1
        return self._data.split(self._sep)[self._index - 1]

    def __repr__(self):
        return self._data.split(self._sep)

    @property
    def iscomplete(self):
        if re.match(self.rex.format(sep=self._sep, fields=self._fields), self._data):
            return True
        return False

    @property
    def artistsort(self):
        return self._data.split(self._sep)[0]

    @property
    def artist(self):
        artist = self._data.split(self._sep)[0]
        a = artist.split(", ", 1)
        if len(a) == 2:
            artist = "{a[1]} {a[0]}".format(a=a)
        return artist

    @staticmethod
    def artistindex(s):
        return re.sub(r"\W+", ".", s)

    @classmethod
    def gettrackfromfile(cls, fp, fields=2, sep=";"):
        for line in iter(fp.readline, ""):
            yield cls(line, fields, sep)


class Default(Track):

    def __init__(self, line, fields=2, sep=";"):
        super(Default, self).__init__(line, fields, sep)

    @property
    def aredatavalid(self):
        return self.datacheck(self._data, self._fields, self._sep)

    @property
    def index(self):
        template = Template(r"1.${year}0000.$index")
        return "{0}.{1}".format(self.artistindex(self._data.split(self._sep)[0]), template.substitute(year=self._data.split(self._sep)[1], index=self._data.split(self._sep)[2]))

    @property
    def year(self):
        return self._data.split(self._sep)[1]

    @property
    def album(self):
        return self._data.split(self._sep)[3]

    @property
    def track(self):
        return self._data.split(self._sep)[4]

    @property
    def totaltracks(self):
        return self._data.split(self._sep)[5]

    @property
    def title(self):
        return self._data.split(self._sep)[6]

    @staticmethod
    def datacheck(s, fields, sep):
        datacorrect = True
        for code in range(1, fields + 1):
            if code == 1:
                break
            elif code == 2:
                break
            elif code == 3:
                break
        return datacorrect


class Bootleg(Track):

    def __init__(self, line, fields=2, sep=";"):
        super(Bootleg, self).__init__(line, fields, sep)

    @property
    def aredatavalid(self):
        return self.datacheck(self._data, self._fields, self._sep)

    @property
    def index(self):
        template = Template(r"2.$year$month$day.$index")
        r = self.date
        if r.succeeded:
            return "{0}.{1}".format(self.artistindex(self._data.split(self._sep)[0]), template.substitute(year=r.date.year, month=r.date.month, day=r.date.day, index=self._data.split(self._sep)[4]))

    @property
    def city(self):
        return self._data.split(self._sep)[1]

    @property
    def country(self):
        return self._data.split(self._sep)[2]

    @property
    def date(self):
        result = namedtuple("result", "succeeded, date")
        date = namedtuple("date", "year month day")
        match = re.match(r"^(\d{4})\-(\d{2})\-(\d{2})$", self._data.split(self._sep)[3])
        if match:
            return result(True, date(match.group(1), match.group(2), match.group(3)))
        return result(False, None)

    @property
    def tour(self):
        return self._data.split(self._sep)[5]

    @property
    def media(self):
        return self._data.split(self._sep)[6]

    @property
    def track(self):
        return self._data.split(self._sep)[7]

    @property
    def totaltracks(self):
        return self._data.split(self._sep)[8]

    @property
    def title(self):
        return self._data.split(self._sep)[9]

    @staticmethod
    def datacheck(s, fields, sep):
        datacorrect = True
        for code in range(1, fields + 1):
            if code == 1:
                break
            elif code == 2:
                break
            elif code == 3:
                break
        return datacorrect


class CustomFormatter(logging.Formatter):

    converter = datetime.fromtimestamp
    default_time_format = "%d/%m/%Y %H:%M:%S"
    default_localizedtime_format = "%Z%z"
    default_format = "%s %s,%03d %s"

    def formatTime(self, record, datefmt=None):
        ct = self.converter(record.created, tz=timezone(DFTTIMEZONE))
        s = self.default_format % (ct.strftime("%A"), ct.strftime(self.default_time_format), record.msecs, ct.strftime(self.default_localizedtime_format))
        if datefmt:
            s = ct.strftime(datefmt)
        return s


class AudioFiles(object):

    OBJ = {"flac": FLAC, "mp3": MP3}

    def __init__(self, coll):
        self._albums = None
        self._tracks = None
        self._coll = None
        self.coll = coll

    def __call__(self, *args, key=None, value=None):

        albums, tracks = deque(), deque()

        #  1. Check "typ".
        if all([arg.lower() not in ["flac", "mp3"] for arg in args]):
            raise ValueError('Invalid filter. {0} received whereas only "flac" and "mp3" are accepted.'.format(list(args)))

        #  2. Check "key".
        k = key
        if key and key.lower() not in ["album", "artist", "title"]:
            raise ValueError('Invalid argument. "{0}" received whereas only "album", "artist" and "title" are accepted.'.format(key))

        #  3. Check "value".
        v = value
        if value:
            if not isinstance(value, Iterable):
                raise ValueError('"{0}" is not iterable.'.format(value))
            if type(value) in [list, tuple]:
                v = "|".join(value)

        #  4. Check both "key" and "value".
        if any([item is not None for item in (key, value)]) and not all([item is not None for item in (key, value)]):
            if not key:
                raise ValueError("Filter key is missing.")
            elif not value:
                raise ValueError("Filter value is missing.")

        #  5. Grab audio metadata.
        regex = re.compile("({0})".format(v), re.IGNORECASE)
        for arg in args:
            for file in self.coll:
                try:
                    audiofil = self.OBJ[arg.lower()](file)
                except MutagenError:
                    continue
                if "artistsort" not in audiofil:
                    continue
                if "albumsort" not in audiofil:
                    continue
                if "titlesort" not in audiofil:
                    continue
                if "artist" not in audiofil:
                    continue
                if "album" not in audiofil:
                    continue
                if "discnumber" not in audiofil:
                    continue
                if "tracknumber" not in audiofil:
                    continue
                if "title" not in audiofil:
                    continue
                search, getfile = regex.search(audiofil[k][0]), True
                if not search:
                    getfile = False
                if getfile:
                    albums.append(("{artistsort}.{albumsort}".format(artistsort=audiofil["artistsort"][0], albumsort=audiofil["albumsort"][0]), audiofil["album"][0]))
                    tracks.append((
                        ("{artistsort}.{albumsort}".format(artistsort=audiofil["artistsort"][0], albumsort=audiofil["albumsort"][0]), audiofil["titlesort"][0]),
                        (
                            audiofil["discnumber"][0],
                            audiofil["tracknumber"][0],
                            audiofil["title"][0],
                            file
                        )
                    ))

        #  6. Set output.
        self._tracks = {itemgetter(0)(item): dict([(itemgetter(1)(itemgetter(0)(track)), (itemgetter(0)(itemgetter(1)(track)),
                                                                                          itemgetter(1)(itemgetter(1)(track)),
                                                                                          itemgetter(2)(itemgetter(1)(track)),
                                                                                          itemgetter(3)(itemgetter(1)(track)))
                                                    )
                                                   for track in sorted(sorted(tracks, key=self.sortedbytracks), key=self.sortedbyalbums)
                                                   if itemgetter(0)(itemgetter(0)(track)) == itemgetter(0)(item)])
                        for item in sorted(set(albums), key=itemgetter(0))}
        self._albums = dict(albums)

        #  7. Yield output.
        for item in sorted(self._tracks):
            yield item, self._albums[item], self._tracks[item]

    @property
    def coll(self):
        return self._coll

    @coll.setter
    def coll(self, arg):
        if not isinstance(arg, Iterable):
            raise ValueError
        self._coll = sorted(arg)

    @property
    def albums(self):
        for album in sorted(self._albums):
            yield self._albums[album]

    @classmethod
    def fromfolder(cls, *args, folder):
        return cls(list(filesinfolder(*args, folder=folder)))

    @staticmethod
    def sortedbytracks(*args):
        return itemgetter(1)(itemgetter(0)(args))

    @staticmethod
    def sortedbyalbums(*args):
        return itemgetter(0)(itemgetter(0)(args))


# ==========
# Functions.
# ==========
@contextmanager
def chgcurdir(d):
    wcdir = os.getcwd()
    os.chdir(d)
    yield
    os.chdir(wcdir)


def validpath(p):
    if not os.path.exists(p):
        raise argparse.ArgumentTypeError('"{0}" doesn\'t exist'.format(p))
    if not os.path.isdir(p):
        raise argparse.ArgumentTypeError('"{0}" is not a directory'.format(p))
    return p


def directorytree(tree):
    """
    :param tree:
    :return:
    """
    for a, b, c in os.walk(tree):
        if c:
            for d in c:
                yield os.path.normpath(os.path.join(a, d))


def dateformat(dt, template):
    """
    :param dt:
    :param template:
    :return:
    """
    return Template(template).substitute(day=dt.strftime("%A").capitalize(),
                                         month=dt.strftime("%B").capitalize(),
                                         d=dt.strftime("%d"),
                                         j=dt.strftime("%j"),
                                         m=dt.strftime("%m"),
                                         y=dt.strftime("%y"),
                                         z=dt.strftime("%z"),
                                         H=dt.strftime("%H"),
                                         M=dt.strftime("%M"),
                                         S=dt.strftime("%S"),
                                         U=dt.strftime("%U"),
                                         W=dt.strftime("%W"),
                                         Y=dt.strftime("%Y"),
                                         Z=dt.strftime("%Z")
                                         )


def filesinfolder(*extensions, folder=os.getcwd()):
    l = []
    if extensions:
        l = sorted([i.lower() for i in extensions])
    for root, folders, files in os.walk(folder):
        for file in files:
            select_file = False
            ext = os.path.splitext(file)[1][1:].lower()
            if not l:
                select_file = True
            elif l and ext in l:
                select_file = True
            if not select_file:
                continue
            else:
                yield os.path.join(root, file)


def getdatetime(epoch, timzon):
    return dateformat(timezone("UTC").localize(datetime.utcfromtimestamp(epoch)).astimezone(timezone(timzon)), TEMPLATE3)


def enumeratesortedlistcontent(thatlist):
    return sorted(enumerate(sorted(thatlist), 1), key=itemgetter(0))


def enumeratetupleslist(thatlist):
    return [(a, b, c) for a, (b, c) in enumerate(sorted(thatlist, key=itemgetter(0)), 1)]


# ==========================
# Jinja2 Customized filters.
# ==========================
def integertostring(intg):
    return str(intg)


def rjustify(s, width):
    return s.rjust(width)


def ljustify(s, width):
    return s.ljust(width)


def repeatelement(elem, n):
    for i in list(itertools.repeat(elem, n)):
        yield i


# def sortedlist(l):
#     for i, j in sorted(l, key=itemgetter(0)):
#         yield i, j


def now():
    return dateformat(UTC.localize(datetime.utcnow()).astimezone(LOCAL), TEMPLATE4)
