# -*- coding: ISO-8859-1 -*-
import io
import os
import locale
import logging
import itertools
from pytz import timezone
from string import Template
from datetime import datetime
from dateutil.tz import gettz
from dateutil.parser import parse
from PIL import Image, TiffImagePlugin

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
                  "defaultprefix"]:
            self._metadata[i] = getattr(self, i)

    @property
    def exif(self):
        return self._exif

    @exif.setter
    def exif(self, value):
        try:
            self._exif = self.getexif(Image.open(value))
        except OSError:
            raise OSError('Can\'t identify "{0}" as an image file.'.format(value))
        else:
            if not self._exif:
                raise ExifError(value, 'Can\'t grab metadata from')
            if 36867 not in self._exif:
                raise ExifError(value, 'Can\'t grab timestamp from')

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
        if 271 in self.exif:
            return self.exif[271]

    @property
    def model(self):
        if 272 in self.exif:
            return self.exif[272]

    @property
    def width(self):
        if 40962 in self.exif:
            return self.exif[40962]

    @property
    def height(self):
        if 40963 in self.exif:
            return self.exif[40963]

    @property
    def copyright(self):
        if 33432 in self.exif:
            return self.exif[33432]

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
            return None
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


# ==========
# Functions.
# ==========
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


def filesinfolder(extensions, folder=os.getcwd()):
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


def integertostring(intg):
    return str(intg)


def rjustify(s, width):
    return s.rjust(width)


def ljustify(s, width):
    return s.ljust(width)


def repeatelement(elem, n):
    for i in list(itertools.repeat(elem, n)):
        yield i


def sortedlist(l):
    for i, j in sorted(l, key=lambda a: a[0]):
        yield i, j


def now():
    return dateformat(UTC.localize(datetime.utcnow()).astimezone(LOCAL), TEMPLATE4)


def getdatetime(epoch1, timzon, epoch2=None):
    if not epoch2:
        epoch2 = epoch1
    for epoch in range(epoch1, epoch2 + 1):
        yield dateformat(timezone("UTC").localize(datetime.utcfromtimestamp(epoch)).astimezone(timezone(timzon)), TEMPLATE3)
