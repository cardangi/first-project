# -*- coding: utf-8 -*-
import io
import os
import locale
import logging
import argparse
import itertools
import logging.handlers
from pytz import timezone
from string import Template
from datetime import datetime
from dateutil.tz import gettz
from operator import itemgetter
from dateutil.parser import parse
from contextlib import contextmanager
from PIL import Image, TiffImagePlugin
from collections import MutableMappings

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
DATABASE = os.path.join(os.path.expandvars("%_COMPUTING%"), "database.db")
# LOG = r"g:\computing\log.log"
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
DFTYEARREGEX = "20[0-2]\d|19[7-9]\d"
DFTMONTHREGEX = "0[1-9]|1[0-2]"
DFTDAYREGEX = "0[1-9]|[12]\d|3[01]"
ACCEPTEDANSWERS = ["N", "Y"]
ARECA = r'"C:\Program Files\Areca\areca_cl.exe"'
MUSIC = "F:\\"
IMAGES = "H:\\"
EXIT = 11
BACK = 12
EXTENSIONS = {"computing": ["py", "json", "yaml", "cmd", "css", "xsl"], "documents": ["doc", "txt", "pdf", "xav"]}


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


class Files(MutableMappings):

    def __init__(self, fil):
        self._fil = None
        self.fil = fil
        self._metadata = {i: getattr(self, i) for i in ["ctime", "mtime", "dirname", "basename", "extension", "parts"]}

    def __getitem__(self, item):
        return self.metadata[item]

    def __setitem__(self, key, value):
        self.metadata[key] = value

    def __delitem__(self, item):
        del self.metadata[item]

    def __len__(self):
        return len(self.metadata)

    def __iter__(self):
        return iter(self.metadata)

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
    def defaultlocation(year, month, day, drive=IMAGES):

        # Cas 1 : "H:\CCYY\MM\DD".
        if year in [2011, 2012]:
            return os.path.normpath(os.path.join(drive, str(year), str(month).zfill(2), str(day).zfill(2)))

        # Cas 2 : "H:\CCYY\MM.DD".
        if year == 2014:
            return os.path.normpath(os.path.join(drive, str(year), "{0}.{1}".format(str(month).zfill(2), str(day).zfill(2))))

        # Cas 3 : "H:\CCYYMM".
        return os.path.normpath(os.path.join(drive, "{0}{1}".format(year, str(month).zfill(2))))


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


class GetPath(argparse.Action):
    """
    Set "destination" attribute with the full path corresponding to the "values".
    """
    destinations = {"documents": os.path.expandvars("%_MYDOCUMENTS%"), "temp": os.path.expandvars("%TEMP%"), "backup": os.path.expandvars("%_BACKUP%")}

    def __init__(self, option_strings, dest, **kwargs):
        super(GetPath, self).__init__(option_strings, dest, **kwargs)

    def __call__(self, parsobj, namespace, values, option_string=None):
        setattr(namespace, self.dest, self.destinations[values])


class GetExtensions(argparse.Action):
    """
    Set "files" attribute with a list of extensions.
    Set "extensions" attribute with a list of extensions to process.
    """
    def __init__(self, option_strings, dest, **kwargs):
        super(GetExtensions, self).__init__(option_strings, dest, **kwargs)

    def __call__(self, parsobj, namespace, values, option_string=None):
        setattr(namespace, self.dest, EXTENSIONS[values])
        setattr(namespace, "extensions", EXTENSIONS[values])


class ExcludeExtensions(argparse.Action):
    """
    Set "exclude" attribute with a list of extensions to exclude.
    Set "extensions" attribute with a list of extensions to process.
    """
    def __init__(self, option_strings, dest, **kwargs):
        super(ExcludeExtensions, self).__init__(option_strings, dest, **kwargs)

    def __call__(self, parsobj, namespace, values, option_string=None):
        setattr(namespace, self.dest, values)
        lext = []
        for ext in getattr(namespace, "files"):
            if ext not in values:
                lext.append(ext)
        setattr(namespace, "extensions", lext)


class RetainExtensions(argparse.Action):
    """
    Set "retain" attribute with a list of extensions to retain.
    Set "extensions" attribute with a list of extensions to process.
    """
    def __init__(self, option_strings, dest, **kwargs):
        super(RetainExtensions, self).__init__(option_strings, dest, **kwargs)

    def __call__(self, parsobj, namespace, values, option_string=None):
        setattr(namespace, self.dest, values)
        lext = []
        for ext in values:
            if ext in getattr(namespace, "files"):
                lext.append(ext)
        setattr(namespace, "extensions", lext)


class IncludeExtensions(argparse.Action):
    """
    Set "include" attribute with a list of extensions to include.
    Set "extensions" attribute with a list of extensions to process.
    """
    def __init__(self, option_strings, dest, **kwargs):
        super(IncludeExtensions, self).__init__(option_strings, dest, **kwargs)

    def __call__(self, parsobj, namespace, values, option_string=None):
        setattr(namespace, self.dest, values)
        lext = getattr(namespace, "extensions")
        for ext in values:
            if ext not in lext:
                lext.append(ext)
        setattr(namespace, "extensions", lext)


# ==========
# Functions.
# ==========
@contextmanager
def chgcurdir(d):
    wcdir = os.getcwd()
    os.chdir(d)
    yield
    os.chdir(wcdir)


def customformatterfactory(pattern=LOGPATTERN):
    return CustomFormatter(pattern)


def customfilehandler(maxbytes, backupcount, encoding=UTF8):
    return logging.handlers.RotatingFileHandler(os.path.join(os.path.expandvars("%_COMPUTING%"), "pythonlog.log"), maxBytes=maxbytes, backupCount=backupcount, encoding=encoding)


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


def now():
    return dateformat(UTC.localize(datetime.utcnow()).astimezone(LOCAL), TEMPLATE4)


# ========
# Parsers.
# ========
zipfileparser = argparse.ArgumentParser()
zipfileparser.add_argument("source", type=validpath)
zipfileparser.add_argument("destination", choices=["documents", "backup", "temp", "onedrive"], action=GetPath)
zipfileparser.add_argument("files", choices=["documents", "computing"], action=GetExtensions)
group = zipfileparser.add_mutually_exclusive_group()
group.add_argument("-e", "--exc", dest="exclude", nargs="*", action=ExcludeExtensions, help="exclude some extensions from the group")
group.add_argument("-r", "--ret", dest="retain", nargs="*", action=RetainExtensions, help="retain some extensions from the group")
zipfileparser.add_argument("-i", "--inc", dest="include", nargs="*", action=IncludeExtensions, help="include some extensions not included in the group")
