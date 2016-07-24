# -*- coding: ISO-8859-1 -*-
__author__ = 'Xavier'


# =================
# Absolute imports.
# =================
import io
import os
import locale
import logging
import itertools
import subprocess
from pytz import timezone
from string import Template
from datetime import datetime
from dateutil.tz import gettz
from dateutil.parser import parse
from PIL import Image, TiffImagePlugin
from sortedcontainers import SortedDict


# ==========================
# Define French environment.
# ==========================
locale.setlocale(locale.LC_ALL, "")


# ==========
# Constants.
# ==========
APPEND = "a"
WRITE = "w"
AUTHOR = "Xavier ROSSET"
CODING = "-*- coding: ISO-8859-1 -*-"
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
DFTYEARREGEX = "20[012]\d"
DFTMONTHREGEX = "0[1-9]|1[0-2]"
DFTDAYREGEX = "0[1-9]|[12][0-9]|3[01]"
ACCEPTEDANSWERS = ["N", "Y"]
ARECA = r'"C:\Program Files\Areca\areca_cl.exe"'
MUSIC = "F:\\"
EXIT = 11
BACK = 12


# ========
# Classes.
# ========

class File:

    attr = ("ctime", "mtime", "dirname", "basename", "extension", "parts")

    def __contains__(self, itm):
        return itm in list(self.metadata.keys())

    def __getitem__(self, itm):
        return self.metadata[itm]

    def __init__(self, fil):
        self.metadata = SortedDict()
        self.exists = os.path.exists(fil)
        if self.exists:
            self.index = 0
            self.metadata["name"] = fil
            self.metadata["dirname"] = os.path.dirname(fil)
            self.metadata["basename"] = os.path.splitext(os.path.basename(fil))[0]
            self.metadata["extension"] = os.path.splitext(fil)[1].strip(".")
            self.metadata["parts"] = os.path.dirname(fil).split("\\")
            self.metadata["ctime"] = int(os.path.getctime(fil))
            self.metadata["mtime"] = int(os.path.getmtime(fil))

    def __iter__(self):
        for k, v in self.metadata.items():
            yield k, v

    def __len__(self):
        return len(self.metadata)

    def __repr__(self):
        return repr(self.metadata)

    def encrypt(self, dst, rcp):
        return subprocess.call(["gpg", "--encrypt", "--output", os.path.join(dst, "{0}.{1}.gpg".format(self.metadata["basename"], self.metadata["extension"])), "--recipient", rcp,
                                os.path.join(self.metadata["dirname"], "{0}.{1}".format(self.metadata["basename"], self.metadata["extension"]))])

    def renameto(self, dirn=None, basn=None):
        dir = self.metadata["dirname"]
        bas = self.metadata["basename"]
        if dirn:
            dir = dirn
        if basn:
            bas = basn
        return os.path.join(dir, "{0}.{1}".format(bas, self.metadata["extension"]))

    def tags(self):
        return list(self.metadata.keys())


class Images(File):

    tzinfos = {"CEST": gettz("Europe/Paris"), "CET": gettz("Europe/Paris")}

    def __init__(self, fil):
        super(Images, self).__init__(fil)
        try:
            self.exif = self.getexif(Image.open(fil))
        except OSError:
            self.exif = {}
        if self.exif:
            if 36867 in self.exif:
                datetime = parse("{} CET".format(self.exif[36867].replace(":", "-", 2)), tzinfos=self.tzinfos)
                self.metadata["localtimestamp"] = int(datetime.timestamp())
                self.metadata["originaldatetime"] = datetime.strftime("%d/%m/%Y %H:%M:%S %Z%z")
                self.metadata["originalyear"] = datetime.strftime("%Y")
                self.metadata["originalmonth"] = datetime.strftime("%m")
                self.metadata["originalday"] = datetime.strftime("%d")
                self.metadata["originalhour"] = datetime.strftime("%H")
                self.metadata["originalminutes"] = datetime.strftime("%M")
                self.metadata["originalseconds"] = datetime.strftime("%S")
                self.metadata["dayoftheyear"] = datetime.strftime("%j")
                self.metadata["dayoftheweek"] = datetime.strftime("%w")
                self.metadata["defaultlocation"] = self.defaultlocation(self.metadata["originalyear"], self.metadata["originalmonth"], self.metadata["originalday"])
                self.metadata["defaultprefix"] = "{}{}".format(self.metadata["originalyear"], str(self.metadata["originalmonth"]).zfill(2))
            if 271 in self.exif:
                self.metadata["make"] = self.exif[271]
            if 272 in self.exif:
                self.metadata["model"] = self.exif[272]
            if 40962 in self.exif:
                self.metadata["width"] = self.exif[40962]
            if 40963 in self.exif:
                self.metadata["height"] = self.exif[40963]
            if 33432 in self.exif:
                self.metadata["copyright"] = self.exif[33432]

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

        defaultdrive = "h:\\"

        # Cas 1 : "h:\CCYY\MM\DD".
        if year in [2011, 2012]:
            return os.path.join(defaultdrive, str(year), str(month).zfill(2), str(day).zfill(2))

        # Cas 2 : "h:\CCYY\MM.DD".
        elif year == 2014:
            return os.path.join(defaultdrive, str(year), "{}.{}".format(str(month).zfill(2), str(day).zfill(2)))

        # Cas 3 : "h:\CCYYMM".
        return os.path.join(defaultdrive, "{}{}".format(year, str(month).zfill(2)))


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


def extensioncount(extensions, folder=os.getcwd()):
    """

    :param extensions:
    :param folder:
    :return:
    """
    d, l = {}, []
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
            if select_file:
                if ext in d:
                    d[ext.upper()] += 1
                else:
                    d[ext.upper()] = 1
    return d


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
