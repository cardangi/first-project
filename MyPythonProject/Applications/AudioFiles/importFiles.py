# -*- coding: ISO-8859-1 -*-
from collections import MutableMapping, MutableSequence, deque, namedtuple
from jinja2 import Environment, FileSystemLoader
from mutagen import File, MutagenError
from itertools import groupby, repeat
from operator import itemgetter, ne
from datetime import datetime
from mutagen.flac import FLAC
from mutagen.mp3 import MP3
from string import Template
from functools import wraps
from pytz import timezone
from shutil import copy2
import subprocess
import argparse
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

    def insert(self, idx, value):
        self.collection.insert(idx, value)

    @property
    def collection(self):
        return self._collection

    @collection.setter
    def collection(self, psargs):
        nt = namedtuple("nt", "artist album codec discnumber tracknumber title file object type")
        for arg in psargs:
            try:
                fil = File(arg)
            except MutagenError:
                continue
            if fil:
                if "audio/flac" in fil.mime:
                    tags = {key.lower(): fil[key][0] for key in fil}
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
                    self._collection.append(nt(tags["artist"], tags["album"], "FLAC", tags["discnumber"], tags["tracknumber"], tags["title"], os.path.normpath(arg), fil, type(fil)))
        self._collection = \
            sorted(
                sorted(
                    sorted(
                        sorted(
                            sorted(self._collection, key=lambda t: t.tracknumber.zfill(2)),
                            key=lambda t: t.discnumber),
                        key=lambda t: t.codec),
                    key=lambda t: t.album),
                key=lambda t: t.artist)

    @classmethod
    def fromfolder(cls, *psargs, folder):
        return cls(*list(shared.filesinfolder(*psargs, folder=folder)))


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
        year, month, day, location, albumsort, titlesort, codecuid = 0, 0, 0, "", "", "", 0

        # Check input tags.
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

        # Initialize dictionnary with input tags.
        self._metadata = {key: psarg[key][0] for key in psarg}

        # Update dictionnary with dynamic tags.
        if isinstance(psarg, FLAC):
            codecuid = 13
        elif isinstance(psarg, MP3):
            codecuid = 2
        match = self.regex.match(self.metadata["album"])
        if match:
            year = int(match.group(2))
        match = self.regex.match(self.metadata["album"])
        if match:
            month = int(match.group(3))
        match = self.regex.match(self.metadata["album"])
        if match:
            day = int(match.group(4))
        match = self.regex.match(self.metadata["album"])
        if match:
            location = match.group(5)
        albumsort = "2.{year}{month:0>2d}{day:0>2d}.1.{code:0>2d}".format(year=year, month=month, day=day, code=codecuid)
        titlesort = "D{discnumber}.T{tracknumber:0>2d}.NYY".format(discnumber=self.metadata["discnumber"], tracknumber=int(self.metadata["tracknumber"]))
        self._metadata.update(list(zip(("year", "month", "day", "location", "albumsort", "titlesort"), (year, month, day, location, albumsort, titlesort))))


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


# ==========
# Arguments.
# ==========
parser = argparse.ArgumentParser()
parser.add_argument("-t", "--test", action="store_true")


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
CURWDIR, TABSIZE1, TABSIZE2 = os.path.expandvars("%_MYMUSIC%"), 10, 4


# ==================
# Initializations 1.
# ==================
header, artists, albums, codecs, index, code, status, curwdir, tracks, files, args, fails, successes, statuss, tmpl, choice, arguments = None, None, None, None, 0, 1, 100, CURWDIR, [], {}, [], [], [], [], "", "", \
                                                                                                                                         parser.parse_args()


# ==================
# Initializations 2.
# ==================
justify, nt1, nt2 = "".join(list(repeat("\n", 3))), namedtuple("nt1", "maintitle step title"), namedtuple("nt2", "file dirname basename extension")


# ===============
# Main algorithm.
# ===============
while True:

    #     ----------------------------------------------
    #  1. Grab available artists from current directory.
    #     ----------------------------------------------
    if code == 1:
        header = shared.Header("import  audio  files", ["Set current directory.", "Set artist.", "Set album", "Set codec", "Import files.", "Run import.", "Tag files", "Exit program."])
        head = header()
        tmpl = template1.render(header=nt1(*head), message=['Current directory is: "{0}"'.format(CURWDIR)])
        successes.clear()
        statuss.clear()
        fails.clear()
        while True:
            print(clearscreen(t=tmpl))
            choice = input("{0}\tWould you like to change the current directory [Y/N]? ".format(justify).expandtabs(TABSIZE1))
            if choice.upper() in shared.ACCEPTEDANSWERS:
                break
        if choice.upper() == "Y":
            tmpl = template1.render(header=nt1(*head))
            while True:
                print(clearscreen(t=tmpl))
                curwdir = input("{0}\tPlease enter directory: ".format(justify).expandtabs(TABSIZE1))
                if curwdir:
                    if not os.path.exists(curwdir):
                        tmpl = template1.render(header=nt1(*head), message=['"{0}" is not a valid directory!'.format(curwdir)])
                        continue
                    if not os.path.isdir(curwdir):
                        tmpl = template1.render(header=nt1(*head), message=['"{0}" is not a valid directory!'.format(curwdir)])
                        continue
                    break
                tmpl = template1.render(header=nt1(*head))
        artists = [(k, list(v)) for k, v in groupby(AudioFiles.fromfolder(folder=curwdir), key=groupbyartist)]
        kartists = [itemgetter(0)(artist) for artist in artists]
        head = header()
        code = 2
        tmpl = template1.render(header=nt1(*head), list1=kartists)
        if not kartists:
            head = shared.Header("import  audio  files", ["Exit program."], 2)()
            code = 99
            tmpl = template1.render(header=nt1(*head), message=["No artists found."])
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
                    tmpl = template1.render(header=nt1(*head), list1=kartists, message=['"{0}" is not a valid input'.format(choice)])
                    continue
                else:
                    if index > len(kartists):
                        tmpl = template1.render(header=nt1(*head), list1=kartists, message=['"{0}" is not a valid input'.format(choice)])
                        continue
                    break
            tmpl = template1.render(header=nt1(*head), list1=kartists)
        albums = [(k, list(v)) for k, v in groupby(artists[index - 1][1], key=groupbyalbum)]
        kalbums = [itemgetter(0)(album) for album in albums]
        head = header()
        code = 3
        tmpl = template1.render(header=nt1(*head), list1=kalbums)
        if not kalbums:
            head = shared.Header("import  audio  files", ["Exit program."], 3)()
            code = 99
            tmpl = template1.render(header=nt1(*head), message=['No albums found.'])
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
                    tmpl = template1.render(header=nt1(*head), list1=kalbums, message=['"{0}" is not a valid input'.format(choice)])
                    continue
                else:
                    if index > len(kalbums):
                        tmpl = template1.render(header=nt1(*head), list1=kalbums, message=['"{0}" is not a valid input'.format(choice)])
                        continue
                    break
            tmpl = template1.render(header=nt1(*head), list1=kalbums)
        codecs = [(k, list(v)) for k, v in groupby(albums[index - 1][1], key=groupbycodec)]
        kcodecs = [itemgetter(0)(codec) for codec in codecs]
        head = header()
        code = 4
        tmpl = template1.render(header=nt1(*head), list1=kcodecs)
        if not kcodecs:
            head = shared.Header("import  audio  files", ["Exit program."], 4)()
            code = 99
            tmpl = template1.render(header=nt1(*head), message=['No codecs found.'])
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
                    tmpl = template1.render(header=nt1(*head), list1=kcodecs, message=['"{0}" is not a valid input'.format(choice)])
                    continue
                else:
                    if index > len(kcodecs):
                        tmpl = template1.render(header=nt1(*head), list1=kcodecs, message=['"{0}" is not a valid input'.format(choice)])
                        continue
                    break
            tmpl = template1.render(header=nt1(*head), list1=kcodecs)
        sources, extensions = [itemgetter(6)(item) for item in codecs[index - 1][1]], [os.path.splitext(itemgetter(6)(item))[1] for item in codecs[index - 1][1]]
        files = [nt2(a, b, c, d) for a, (b, c), d in list(zip(sources,
                                                              [(template2.substitute(year=track["year"],
                                                                                     month="{0:0>2d}".format(track["month"]),
                                                                                     day="{0:0>2d}".format(track["day"]),
                                                                                     location=track["location"],
                                                                                     disc=track["discnumber"]),
                                                                "{0}.{1}".format(track["albumsort"], track["titlesort"])) for track in map(getattributes, [itemgetter(7)(item) for item in codecs[index - 1][1]])
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
        logger.debug("----------")
        logger.debug("Arguments.")
        logger.debug("----------")
        for num, (path, dirname, basename, extension) in enumerate(files, 1):
            logger.debug("{0:>3d}. {1}".format(num, path))
            logger.debug("\t{0}".format(dirname).expandtabs(5))
            logger.debug("\t{0}".format(basename).expandtabs(5))
            logger.debug("\t{0}".format(extension).expandtabs(5))
        head = header()
        code = 5
        tmpl = template1.render(header=nt1(*head),
                                list2=[
                                    (
                                        "Source\t\t: {0}".format(itemgetter(0)(item)).expandtabs(TABSIZE2),
                                        "Destination\t: {0}{1}".format(os.path.join(itemgetter(1)(item), itemgetter(2)(item)), itemgetter(3)(item)).expandtabs(TABSIZE2)
                                    )
                                    for item in files],
                                trailer=["{0:>3d} files ready to be imported.".format(len(files))]
                                )
        if not sources:
            head = shared.Header("import  audio  files", ["Exit program."], 5)()
            code = 99
            tmpl = template1.render(header=nt1(*head), message=['No files found.'])

    #     -------------
    #  5. Import files.
    #     -------------
    elif code == 5:
        while True:
            print(clearscreen(t=tmpl))
            choice = input("{0}\tWould you like to import files [Y/N]? ".format(justify).expandtabs(TABSIZE1))
            if choice.upper() in shared.ACCEPTEDANSWERS:
                break
        head = header()
        code = 6
        if choice.upper() == "Y":
            args.extend(files)
        elif choice.upper() == "N" and not args:
            head = shared.Header("import  audio  files", ["Exit program."], 6)()
            code = 99
        tmpl = template1.render(header=nt1(*head))

    #     -----------
    #  6. Run import.
    #     -----------
    elif code == 6:
        while True:
            print(clearscreen(t=tmpl))
            choice = input("{0}\tWould you like to run import [Y/N]? ".format(justify).expandtabs(TABSIZE1))
            if choice.upper() in shared.ACCEPTEDANSWERS:
                break
        head = header()
        code = 7
        tmpl = template1.render(header=nt1(*head))

        # --> 1. Don't run import.
        if choice.upper() == "N":
            head = shared.Header("import  audio  files", ["Exit program."], 7)()
            code = 99
            tmpl = template1.render(header=nt1(*head))

        # --> 2. Run import.
        elif choice.upper() == "Y":
            logger.debug("----------")
            logger.debug("Arguments.")
            logger.debug("----------")
            for num, (path, dirname, basename, extension) in enumerate(args, 1):
                logger.debug("{0:>3d}. {1}".format(num, path))
                logger.debug("\t{0}".format(dirname).expandtabs(5))
                logger.debug("\t{0}".format(basename).expandtabs(5))
                logger.debug("\t{0}".format(extension).expandtabs(5))

            # --> 2.a. Test mode.
            if arguments.test:
                logger.debug("----------")
                logger.debug("Arguments.")
                logger.debug("----------")
                for num, (path, dirname, basename, extension) in enumerate(args, 1):
                    dst = "{0}{1}".format(os.path.join(dirname, basename), extension)
                    logger.debug("{0:>3d}. Source     : {1}".expandtabs(5).format(num, path))
                    logger.debug("\tDestination: {0}".expandtabs(5).format(dst))
                    statuss.append(0)

            # --> 2.b. Copy mode.
            elif not arguments.test:
                logger.debug("Start copying files.")

                for item in args:
                    dst = "{0}{1}".format(os.path.join(item.dirname, item.basename), item.extension)
                    while True:
                        try:
                            copy2(src="{0}".format(item.file), dst=dst)
                        except FileNotFoundError:
                            logger.debug('"FileNotFound" error raised. Create "{0}"'.format(item.dirname))
                            os.makedirs(item.dirname)
                        except FileExistsError:
                            logger.debug('"FileExists" error raised.')
                            statuss.append(100)
                            fails.append(dst)
                            break
                        else:
                            statuss.append(0)
                            successes.append(dst)
                            break

                logger.debug("End copying files.")
                if successes:
                    logger.debug("----------")
                    logger.debug("Successes.")
                    logger.debug("----------")
                    for num, file in enumerate(successes, 1):
                        logger.debug("{0:>3d}. {1}".format(num, file))
                if fails:
                    logger.debug("------")
                    logger.debug("Fails.")
                    logger.debug("------")
                    for num, file in enumerate(fails, 1):
                        logger.debug("{0:>3d}. {1}".format(num, file))

            # -> 2.c. All commands failed.
            if all(map(ne, statuss, repeat(0))):
                head = shared.Header("import  audio  files", ["Exit program."], 7)()
                code = 99
                tmpl = template1.render(header=nt1(*head))

            # --> 2.d. At least one command failed.
            elif any(map(ne, statuss, repeat(0))):
                tmpl = template1.render(header=nt1(*head))

    #     ----------
    #  7. Tag files.
    #     ----------
    elif code == 7:
        while True:
            print(clearscreen(t=tmpl))
            choice = input("{0}\tWould you like to tag copied files [Y/N]? ".format(justify).expandtabs(TABSIZE1))
            if choice.upper() in shared.ACCEPTEDANSWERS:
                break
        head = shared.Header("import  audio  files", ["Exit program."], 8)()
        code = 99
        tmpl = template1.render(header=nt1(*head))
        if choice.upper() == "Y":
            for file in successes:
                try:
                    track = FLAC(file)
                    # track = ExtendedTrack(file, codecs[index - 1][1])
            #     except MutagenError:
            #         pass
            #     else:
            #         track.update(**{"artistsort": mapartist(artists[index - 1][1]), "albumartistsort": mapartist(artists[index - 1][1])})
                except MutagenError:
                    pass
                else:
                    track["artistsort"] = "Springsteen, Bruce"
                    track["albumartistsort"] = "Springsteen, Bruce"
                    track.save()
            code = 99
            tmpl = template1.render(header=nt1(*head))

    #     -------------
    #  8. Exit program.
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


# ============
# End logging.
# ============
logger.info('END "%s".' % (os.path.basename(__file__),))


# =============
# Exit program.
# =============
sys.exit(status)
