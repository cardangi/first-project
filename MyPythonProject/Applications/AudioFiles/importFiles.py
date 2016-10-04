# -*- coding: ISO-8859-1 -*-
from collections import MutableMapping, MutableSequence, Counter, deque, namedtuple
from jinja2 import Environment, FileSystemLoader
from mutagen import File, MutagenError
from itertools import groupby, repeat
from operator import itemgetter, ne
from datetime import datetime
from string import Template
from functools import wraps
from pytz import timezone
from shutil import copy2
import subprocess
import logging
import locale
import sys
import os
import re
from .. import shared

__author__ = 'Xavier ROSSET'


# ==========================
# Define French environment.
# ==========================
locale.setlocale(locale.LC_ALL, "")


# ========
# Classes.
# ========
class TagError(MutagenError):
    def __init__(self, tag, msg):
        self.tag = tag
        self.msg = msg


class AudioFiles(MutableSequence):
    """
    Traite une liste de fichiers audio.
    Retourne une liste de tuples respectant le schéma suivant : [("artist1", "album1", "FLAC", 1, 1, "title1", file1, instance1), ("artist1", "album1", "FLAC", 1, 2, "title2", file2, instance2)]
    Propose une interface de liste.
    """

    def __init__(self, *psargs):
        self._collection = deque()
        self.collection = psargs

    def __getitem__(self, item):
        return self.collection[item]

    def __setitem__(self, key, value):
        self.collection[key] = value

    def __delitem__(self, key):
        del self.collection[key]

    def __len__(self):
        return len(self.collection)

    def insert(self, index, value):
        self.collection.insert(index, value)

    @property
    def collection(self):
        return self._collection

    @collection.setter
    def collection(self, psargs):
        nt = namedtuple("nt", "artist album codec discnumber tracknumber title file object")
        for arg in psargs:
            try:
                file = File(arg)
            except MutagenError:
                continue
            if file:
                if "audio/flac" in file.mime:
                    tags = {key.lower(): file[key][0] for key in file}
                    if "artist" not in tags:
                        continue
                    if "album" not in tags:
                        continue
                    if "discnumber" not in tags:
                        continue
                    if "tracknumber" not in tags:
                        continue
                    if "title" not in tags:
                        continue
                    self._collection.append(nt(tags["artist"], tags["album"], "FLAC", tags["discnumber"], tags["tracknumber"], tags["title"], os.path.normpath(arg), file))
        self._collection = sorted(sorted(sorted(sorted(sorted(sorted(self._collection, key=self.sortedbytrack), key=self.sortedbydisc), key=self.sortedbycodec), key=self.sortedbyalbum), key=self.sortedbyartist))

    @classmethod
    def fromfolder(cls, *psargs, folder):
        return cls(*list(shared.filesinfolder(*psargs, folder=folder)))

    @staticmethod
    def sortedbytrack(t):
        return t.tracknumber.zfill(2)

    @staticmethod
    def sortedbydisc(t):
        return t.discnumber

    @staticmethod
    def sortedbycodec(t):
        return t.codec

    @staticmethod
    def sortedbyalbum(t):
        return t.album

    @staticmethod
    def sortedbyartist(t):
        return t.artist


class Track(MutableMapping):
    """
    Traite un objet fichier audio créé préalablement par l'application Mutagen.
    Retourne la liste des tags dans un dictionnaire ainsi que les attributs "albumsort", "discnumber", "titlesort", "year", "month", "day" et "location".
    Propose une interface de dictionnaire.
    """
    regex = re.compile(r"^(({year})/({month})/({day})) ([^,]+,  [a-z]+)$".format(year=shared.DFTYEARREGEX,  month=shared.DFTMONTHREGEX, day=shared.DFTDAYREGEX), re.IGNORECASE)

    def __init__(self, psarg):
        self._metadata = dict()
        self.metadata = psarg

    def __getitem__(self, item):
        return self.metadata[item]

    def __setitem__(self, key, value):
        self.metadata[key] = value

    def __delitem__(self, key):
        del self.metadata[key]

    def __len__(self):
        return len(self.metadata)

    def __iter__(self):
        return iter(self.metadata)

    @property
    def metadata(self):
        return self._metadata

    @metadata.setter
    def metadata(self, psarg):
        if "artist" not in psarg:
            raise TagError("artist", "isn\'t available.")
        if "album" not in psarg:
            raise TagError("album", "isn\'t available.")
        if not self.regex.match(psarg["album"][0]):
            raise TagError("album", "doesn\'t respect the expected pattern.")
        if "discnumber" not in psarg:
            raise TagError("discnumber", "isn\'t available.")
        if "tracknumber" not in psarg:
            raise TagError("tracknumber", "isn\'t available.")
        self._metadata = {key: psarg[key][0] for key in psarg}

    @property
    def albumsort(self):
        return "2.{year}{month:0>2d}{day:0>2d}.1.13".format(year=self.year, month=self.month, day=self.day)

    @property
    def discnumber(self):
        return self.metadata["discnumber"]

    @property
    def titlesort(self):
        return "D{discnumber}.T{tracknumber:0>2d}.NYY".format(discnumber=self.metadata["discnumber"], tracknumber=int(self.metadata["tracknumber"]))

    @property
    def year(self):
        match = self.regex.match(self.metadata["album"])
        if match:
            return int(match.group(2))

    @property
    def month(self):
        match = self.regex.match(self.metadata["album"])
        if match:
            return int(match.group(3))

    @property
    def day(self):
        match = self.regex.match(self.metadata["album"])
        if match:
            return int(match.group(4))

    @property
    def location(self):
        match = self.regex.match(self.metadata["album"])
        if match:
            return match.group(5)


# ==========
# Functions.
# ==========
def renderheader(func):
    @wraps(func)
    def wrapper(t):
        func()
        return t
    return wrapper


@renderheader
def clearscreen():
    subprocess.run("CLS", shell=True)


def directorytree(directory, rex=None):
    for root, folders, files in os.walk(directory):
        for file in files:
            if rex:
                if not rex.search(os.path.join(root, file)):
                    continue
            yield os.path.join(root, file)


def getattributes(obj):
    try:
        tags = Track(obj)
    except TagError:
        return None
    return tags


def groupbyartist(t):
    return t.artist


def groupbyalbum(t):
    return t.album


def groupbycodec(t):
    return t.codec


# ========
# Logging.
# ========
logger = logging.getLogger("%s.%s" % (__package__, os.path.basename(__file__)))


# ==============
# Start logging.
# ==============
logger.info("{0:=^140s}".format(" {0} ".format(shared.dateformat(datetime.now(tz=timezone(shared.DFTTIMEZONE)), shared.TEMPLATE1))))
logger.info('START "%s".' % (os.path.basename(__file__),))


# ======================
# Jinja2 environment(s).
# ======================
environment = Environment(loader=FileSystemLoader(os.path.join(os.path.expandvars("%_PYTHONPROJECT%"), "Applications", "AudioFiles", "Templates"), encoding=shared.DFTENCODING),
                          trim_blocks=True,
                          lstrip_blocks=True)


# ==========================
# Jinja2 global variable(s).
# ==========================
environment.globals["now"] = shared.now()
environment.globals["copyright"] = shared.COPYRIGHT


# ========================
# Jinja2 custom filter(s).
# ========================
environment.filters["integertostring"] = shared.integertostring
environment.filters["repeatelement"] = shared.repeatelement
environment.filters["ljustify"] = shared.ljustify
environment.filters["rjustify"] = shared.rjustify


# ===================
# Jinja2 template(s).
# ===================
template1 = environment.get_template("T1")


# ================
# Local templates.
# ================
template2 = Template(r"F:\S\Springsteen, Bruce\2\$year\$month.$day - $location\CD$disc\1.Free Lossless Audio Codec")


# ==========
# Constants.
# ==========
CURWDIR, TABSIZE1, TABSIZE2 = os.path.join(os.path.expandvars("%_MYMUSIC%"), r"Bruce Springsteen & The E Street Band"), 10, 4


# ==================
# Initializations 1.
# ==================
header, artists, albums, codecs, index, code, status, curwdir, tracks, files, args, statuss, tmpl, choice = None, None, None, None, 0, 1, 100, CURWDIR, [], {}, [], [], "", ""


# ==================
# Initializations 2.
# ==================
justify, nt = "".join(list(repeat("\n", 3))), namedtuple("nt", "maintitle step title")


# ===============
# Main algorithm.
# ===============
while True:

    #     ----------------------------------------------
    #  1. Grab available artists from current directory.
    #     ----------------------------------------------
    if code == 1:
        header = shared.Header("import  audio  files", ["Set current directory.", "Set artist.", "Set album", "Set codec", "Import files.", "Run import.", "Exit program."])
        head = header()
        tmpl = template1.render(header=nt(*head), message=['Current directory is: "{0}"'.format(CURWDIR)])
        tracks.clear()
        statuss.clear()
        while True:
            print(clearscreen(t=tmpl))
            choice = input("{0}\tWould you like to change the current directory [Y/N]? ".format(justify).expandtabs(TABSIZE1))
            if choice.upper() in shared.ACCEPTEDANSWERS:
                break
        if choice.upper() == "Y":
            tmpl = template1.render(header=nt(*head))
            while True:
                print(clearscreen(t=tmpl))
                curwdir = input("{0}\tPlease enter directory: ".format(justify).expandtabs(TABSIZE1))
                if curwdir:
                    if not os.path.exists(curwdir):
                        tmpl = template1.render(header=nt(*head), message=['"{0}" is not a valid directory!'.format(curwdir)])
                        continue
                    if not os.path.isdir(curwdir):
                        tmpl = template1.render(header=nt(*head), message=['"{0}" is not a valid directory!'.format(curwdir)])
                        continue
                    break
                tmpl = template1.render(header=nt(*head))
        artists = [(k, list(v)) for k, v in groupby(AudioFiles.fromfolder(folder=curwdir), key=groupbyartist)]
        kartists = [itemgetter(0)(artist) for artist in artists]
        head = header()
        code = 2
        tmpl = template1.render(header=nt(*head), list1=kartists)
        if not kartists:
            head = shared.Header("import  audio  files", ["Exit program."], 2)()
            code = 99
            tmpl = template1.render(header=nt(*head), message=["No artists found."])
        logger.debug("--------------")
        logger.debug("Found artists.")
        logger.debug("--------------")
        for num, artist in enumerate(kartists, 1):
            logger.debug("{0:>3d}. {1}".format(num, artist))

    #     ----------------------------------
    #  2. Grab available albums from artist.
    #     ----------------------------------
    elif code == 2:
        while True:
            print(clearscreen(t=tmpl))
            choice = input("{0}\tPlease choose artist: ".format(justify).expandtabs(TABSIZE1))
            if choice:
                try:
                    index = int(choice)
                except ValueError:
                    tmpl = template1.render(header=nt(*head), list1=kartists, message=['"{0}" is not a valid input'.format(choice)])
                    continue
                else:
                    if index > len(kartists):
                        tmpl = template1.render(header=nt(*head), list1=kartists, message=['"{0}" is not a valid input'.format(choice)])
                        continue
                    break
            tmpl = template1.render(header=nt(*head), list1=kartists)
        albums = [(k, list(v)) for k, v in groupby(artists[index - 1][1], key=groupbyalbum)]
        kalbums = [itemgetter(0)(album) for album in albums]
        head = header()
        code = 3
        tmpl = template1.render(header=nt(*head), list1=kalbums)
        if not kalbums:
            head = shared.Header("import  audio  files", ["Exit program."], 3)()
            code = 99
            tmpl = template1.render(header=nt(*head), message=['No albums found.'])
        logger.debug("-------------")
        logger.debug("Found albums.")
        logger.debug("-------------")
        for num, album in enumerate(kalbums, 1):
            logger.debug("{0:>3d}. {1}".format(num, album))

    #     ---------------------------------
    #  3. Grab available codecs from album.
    #     ---------------------------------
    elif code == 3:
        while True:
            print(clearscreen(t=tmpl))
            choice = input("{0}\tPlease choose album: ".format(justify).expandtabs(TABSIZE1))
            if choice:
                try:
                    index = int(choice)
                except ValueError:
                    tmpl = template1.render(header=nt(*head), list1=kalbums, message=['"{0}" is not a valid input'.format(choice)])
                    continue
                else:
                    if index > len(kalbums):
                        tmpl = template1.render(header=nt(*head), list1=kalbums, message=['"{0}" is not a valid input'.format(choice)])
                        continue
                    break
            tmpl = template1.render(header=nt(*head), list1=kalbums)
        codecs = [(k, list(v)) for k, v in groupby(albums[index - 1][1], key=groupbycodec)]
        kcodecs = [itemgetter(0)(codec) for codec in codecs]
        head = header()
        code = 4
        tmpl = template1.render(header=nt(*head), list1=kcodecs)
        if not kcodecs:
            head = shared.Header("import  audio  files", ["Exit program."], 4)()
            code = 99
            tmpl = template1.render(header=nt(*head), message=['No codecs found.'])
        logger.debug("-------------")
        logger.debug("Found codecs.")
        logger.debug("-------------")
        for num, codec in enumerate(kcodecs, 1):
            logger.debug("{0:>3d}. {1}".format(num, codec))

    #     --------------------------------
    #  4. Grab available files from codec.
    #     --------------------------------
    elif code == 4:
        while True:
            print(clearscreen(t=tmpl))
            choice = input("{0}\tPlease choose codec: ".format(justify).expandtabs(TABSIZE1))
            if choice:
                try:
                    index = int(choice)
                except ValueError:
                    tmpl = template1.render(header=nt(*head), list1=kcodecs, message=['"{0}" is not a valid input'.format(choice)])
                    continue
                else:
                    if index > len(kcodecs):
                        tmpl = template1.render(header=nt(*head), list1=kcodecs, message=['"{0}" is not a valid input'.format(choice)])
                        continue
                    break
            tmpl = template1.render(header=nt(*head), list1=kcodecs)
        sources = [itemgetter(6)(item) for item in codecs[index - 1][1]]
        extensions = [os.path.splitext(itemgetter(6)(item))[1] for item in codecs[index - 1][1]]
        destinations = [(a, b, c, d) for a, (b, c), d in list(zip(sources,
                                                                  [(template2.substitute(year=track.year,
                                                                                         month="{0:0>2d}".format(track.month),
                                                                                         day="{0:0>2d}".format(track.day),
                                                                                         location=track.location,
                                                                                         disc=track.discnumber
                                                                                         ),
                                                                    "{0}.{1}".format(track.albumsort, track.titlesort)) for track in map(getattributes, [itemgetter(7)(item) for item in codecs[index - 1][1]])
                                                                   if track],
                                                                  extensions
                                                                  )
                                                              )
                        ]
        logger.debug("------")
        logger.debug("Files.")
        logger.debug("------")
        for num, source in enumerate(sources, 1):
            logger.debug("{0:>3d}. {1}".format(num, source))
        logger.debug("-------------")
        logger.debug("Destinations.")
        logger.debug("-------------")
        for num, (a, b, c, d) in enumerate(destinations, 1):
            logger.debug("{0:>3d}. {1}".format(num, a))
            logger.debug("\t{0}".format(b).expandtabs(5))
            logger.debug("\t{0}".format(c).expandtabs(5))
            logger.debug("\t{0}".format(d).expandtabs(5))
        head = header()
        code = 99
        tmpl = template1.render(header=nt(*head),
                                list2=[
                                    (
                                        "Source\t\t: {0}".format(itemgetter(0)(item)).expandtabs(TABSIZE2),
                                        "Destination\t: {0}{1}".format(os.path.join(itemgetter(1)(item), itemgetter(2)(item)), itemgetter(3)(item)).expandtabs(TABSIZE2)
                                    )
                                    for item in destinations],
                                trailer=["{0:>3d} files ready to be imported.".format(len(destinations))]
                                )
        if not sources:
            head = shared.Header("import  audio  files", ["Exit program."], 5)()
            code = 99
            tmpl = template1.render(header=nt(*head), message=['No files found.'])

    #     -------------
    #  5. Exit program.
    #     -------------
    elif code == 99:
        while True:
            print(clearscreen(t=tmpl))
            choice = input("{0}\tWould you like to exit program [Y/N]? ".format(justify).expandtabs(TABSIZE1))
            if choice.upper() in shared.ACCEPTEDANSWERS:
                break
        if choice.upper() == "N":
            code = 1
        elif choice.upper() == "Y":
            status = 99
            break


# =============
# Exit program.
# =============
sys.exit(status)
