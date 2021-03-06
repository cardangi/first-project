# -*- coding: utf-8 -*-
import re
import io
import os
import locale
import logging
import zipfile
import argparse
import itertools
import logging.handlers
from pytz import timezone
from string import Template
from itertools import repeat
from datetime import datetime
from dateutil.tz import gettz
from operator import itemgetter
from dateutil.parser import parse
from PIL import Image, TiffImagePlugin
from collections import MutableMapping
from contextlib import ContextDecorator

__author__ = 'Xavier ROSSET'


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
ARECA = os.path.join(os.path.expandvars("%PROGRAMFILES%"), "Areca", "areca_cl.exe")
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
MUSIC = "F:\\"
IMAGES = "H:\\"
EXTENSIONS = {"computing": ["py", "json", "yaml", "cmd", "css", "xsl"], "documents": ["doc", "txt", "pdf", "xav"], "music": ["ape", "mp3", "m4a", "flac", "ogg"]}
ZONES = ["US/Pacific", "US/Eastern", "Indian/Mayotte", "Asia/Tokyo", "Australia/Sydney"]
PASSWORD = r"F*HJDa$_+t"
NAS = r"192.168.1.20"


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


class Files(MutableMapping):

    def __init__(self, fil):
        self._fil = None
        self.fil = fil
        self._metadata = {i: getattr(self, i) for i in ["ctime", "mtime", "dirname", "basename", "extension", "parts"]}

    def __getitem__(self, item):
        return self._metadata[item]

    def __setitem__(self, key, value):
        self._metadata[key] = value

    def __delitem__(self, key):
        del self._metadata[key]

    def __len__(self):
        return len(self._metadata)

    def __iter__(self):
        return iter(self._metadata)

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


class ChangeRemoteCurrentDirectory(ContextDecorator):
    """
    Context manager to change the current directory from a remote system.
    Use default FTPLIB library.
    """
    def __init__(self, ftpobj, directory):
        self._dir = directory
        self._ftpobj = ftpobj
        self._cwd = ftpobj.pwd()

    def __enter__(self):
        self._ftpobj.cwd(self._dir)
        return self

    def __exit__(self, *exc):
        self._ftpobj.cwd(self._cwd)


class AlternativeChangeRemoteCurrentDirectory(ContextDecorator):
    """
    Context manager to change the current directory from a remote system.
    Use FTPUTIL library.
    """
    def __init__(self, ftpobj, directory):
        self._dir = directory
        self._ftpobj = ftpobj
        self._cwd = ftpobj.getcwd()

    def __enter__(self):
        self._ftpobj.chdir(self._dir)
        return self

    def __exit__(self, *exc):
        self._ftpobj.chdir(self._cwd)


class ChangeLocalCurrentDirectory(ContextDecorator):
    """
    Context manager to change the current directory from a local system.
    """
    def __init__(self, directory):
        self._dir = directory
        self._cwd = os.getcwd()

    def __enter__(self):
        os.chdir(self._dir)
        return self

    def __exit__(self, *exc):
        os.chdir(self._cwd)


class GlobalInterface(object):

    def __init__(self, *inputs):
        self._answer = None
        self._inputs = inputs
        self._levels = len(inputs)
        self._input = inputs[0]
        self._level = 1
        self._index = 0
        self._step = 0

    def __iter__(self):
        return self

    def __next__(self):

        # Stop iteration once last level is exhausted.
        if self._level >= self._levels and self._index >= len(self._input):
            raise StopIteration

        # Load next level once previous level is exhausted.
        if self._level > 0 and self._index >= len(self._input):
            self._input = self._inputs[self._level].get(self._answer)
            if not self._input:
                raise StopIteration
            self._level += 1
            self._index = 0

        # Return expected input.
        self._index += 1
        self._step += 1
        return self._input[self._index - 1]

    @property
    def step(self):
        return self._step

    @property
    def answer(self):
        return self._answer

    @answer.setter
    def answer(self, value):
        self._answer = value


# ===========================
# Customized parsing actions.
# ===========================
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
        setattr(namespace, self.dest, values)
        lext = []
        for file in values:
            lext.extend(EXTENSIONS[file])
        setattr(namespace, "extensions", lext)


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
        for ext in getattr(namespace, "extensions"):
            if ext not in values:
                lext.append(ext)
        setattr(namespace, "extensions", lext)


class KeepExtensions(argparse.Action):
    """
    Set "retain" attribute with a list of extensions to retain.
    Set "extensions" attribute with a list of extensions to process.
    """
    def __init__(self, option_strings, dest, **kwargs):
        super(KeepExtensions, self).__init__(option_strings, dest, **kwargs)

    def __call__(self, parsobj, namespace, values, option_string=None):
        setattr(namespace, self.dest, values)
        lext = []
        for ext in values:
            if ext in getattr(namespace, "extensions"):
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


class SetEndSeconds(argparse.Action):
    """
    Set "end" attribute.
    """
    def __init__(self, option_strings, dest, **kwargs):
        super(SetEndSeconds, self).__init__(option_strings, dest, **kwargs)

    def __call__(self, parsobj, namespace, values, option_string=None):
        setattr(namespace, self.dest, values)
        if not values:
            setattr(namespace, self.dest, getattr(namespace, "start"))


class SetUID(argparse.Action):
    """
    Set "end" attribute.
    Set "uid" attribute.
    """

    def __init__(self, option_strings, dest, **kwargs):
        super(SetUID, self).__init__(option_strings, dest, **kwargs)

    def __call__(self, parsobj, namespace, values, option_string=None):
        setattr(namespace, self.dest, values)
        setattr(namespace, "uid", list(range(getattr(namespace, "start"), values + 1)))


# ==========
# Functions.
# ==========
def customformatterfactory(pattern=LOGPATTERN):
    return CustomFormatter(pattern)


def customfilehandler(maxbytes, backupcount, encoding=UTF8):
    return logging.handlers.RotatingFileHandler(os.path.join(os.path.expandvars("%_COMPUTING%"), "pythonlog.log"), maxBytes=maxbytes, backupCount=backupcount, encoding=encoding)


def now():
    return dateformat(UTC.localize(datetime.utcnow()).astimezone(LOCAL), TEMPLATE4)


def validpath(p):
    if not os.path.exists(p):
        raise argparse.ArgumentTypeError('"{0}" doesn\'t exist'.format(p))
    if not os.path.isdir(p):
        raise argparse.ArgumentTypeError('"{0}" is not a directory'.format(p))
    if not os.access(p, os.R_OK):
        raise ValueError('"{0}" is not a readable directory'.format(p))
    return p


def validdb(db):
    if not os.path.exists(db):
        raise argparse.ArgumentTypeError('"{0}" doesn\'t exist.'.format(db))
    return db


def validseconds(seconds):
    if not re.match(r"^\d{10}$", seconds):
        raise argparse.ArgumentTypeError('"{0}" is not a valid seconds number'.format(seconds))
    return int(seconds)


def dateformat(dt, template):
    """
    Return a human readable date from a datetime object.
    :param dt: datetime object.
    :param template: template used to return datetime oject.
    :return: human readable date.
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


def filesinfolder(*extensions, folder, excluded=None):
    """
    Return a generator object yielding files stored in "folder" having extension enumerated in "extensions".
    :param extensions: not mandatory list of extension(s) to filter files.
    :param folder: folder to walk through.
    :param excluded: list of folder(s) to exclude.
    :return: generator object.
    """
    logger = logging.getLogger("Default.{0}.filesinfolder".format(__name__))

    # --> Regular expression for folder(s) exclusion.
    regex1 = None
    if excluded:
        regex1 = re.compile(r"(?:{0})".format("|".join(map(os.path.normpath, map(os.path.join, repeat(folder), excluded))).replace("\\", r"\\").replace("$", r"\$")), re.IGNORECASE)

    # --> Walk through folder.
    for root, folders, files in os.walk(folder):

        # Regular expression for extension(s) inclusion.
        rex2 = r"\.[a-z0-9]{3,}$"
        if extensions:
            rex2 = r"\.(?:{0})$".format("|".join(extensions))
        regex2 = re.compile(rex2, re.IGNORECASE)

        # Yield file(s) if not excluded.
        for file in files:
            if regex1 and regex1.match(root):
                continue
            if not regex2.match(os.path.splitext(file)[1]):
                continue
            yield os.path.join(root, file)


def getdatefromseconds(start, stop, zone=DFTTIMEZONE):
    """
    Return a map object yielding human readable dates corresponding to a range of seconds since the epoch.
    :param start: range start seconds.
    :param stop: range stop seconds.
    :param zone: not mandatory time zone appended to the map object.
    :return: map object.
    """
    def func1(item, iterable, pos=0):
        iterable.insert(pos, item)
        return iterable

    def func2(item, iterable, pos=0):
        iterable.insert(pos, dateformat(timezone("UTC").localize(datetime.utcfromtimestamp(item)), TEMPLATE3))
        return iterable

    def func3(ts, tz):
        return dateformat(timezone("UTC").localize(datetime.utcfromtimestamp(ts)).astimezone(timezone(tz)), TEMPLATE3)

    if start > stop:
        raise ValueError("Start epoch {0} must be lower than or equal to end epoch {1}".format(start, stop))
    seconds, zones = range(start, stop + 1), list(ZONES)
    zones.insert(2, zone)
    return map(func2, seconds, map(func1, seconds, (list(i) for i in zip(*(map(func3, seconds, repeat(zone)) for zone in zones)))), repeat(1))


def interface(obj):
    for inp, dest in obj:
        while True:
            value = input("{0}. {1}: ".format(obj.step, inp))
            try:
                setattr(obj, dest, value)
                setattr(obj, "answer", value)
            except ValueError:
                continue
            break
    return obj


def zipfiles(archive, *files):
    logger = logging.getLogger("{0}.zipfiles".format(__name__))
    if not os.path.exists(os.path.dirname(archive)):
        raise OSError('"{0}" doesn\'t exist. Please enter an existing directory.'.format(os.path.dirname(archive)))
    with zipfile.ZipFile(archive, "w") as thatzip:
        logger.info('"{0}" used as ZIP file.'.format(archive))
        for file in files:
            if os.path.exists(file):
                thatzip.write(file, arcname=os.path.basename(file))
                logger.info('"{0}" successfully written.'.format(file))
                continue
            logger.info('Failed to write "{0}".'.format(file))


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
    for i in itertools.repeat(elem, n):
        yield i
