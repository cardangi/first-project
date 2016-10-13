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


def mapartistsort(art):
    return ARTISTSORT.get(art.lower(), art)


def mapartist(art):
    return ARTIST.get(art.lower(), art)


def maplanguage(art):
    return LANGUAGES.get(art.lower(), "English")


def log1(s, char="-"):
    logger.debug(char*len(s))
    yield s
    logger.debug(char*len(s))


def log2(iterable):
    for numb, item in enumerate(iterable, 1):
        yield "{0:>3d}. {1}".format(numb, item)


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
CURWDIR, TABSIZE1, TABSIZE2, ARTIST, ARTISTSORT, LANGUAGES = os.path.expandvars("%_MYMUSIC%"), 10, 4, \
                                                             {"bruce springsteen & the e street band": "Bruce Springsteen"}, \
                                                             {"bruce springsteen & the e street band": "Springsteen, Bruce"}, \
                                                             {"bruce springsteen & the e street band": "English"}


# ==================
# Initializations 1.
# ==================
header, artists, albums, codecs, discs, files, successes, args, index, code, status, curwdir, fails, statuss, tmpl, choice, arguments = None, None, None, None, None, None, None, None, 0, 1, 100, CURWDIR, [], [], \
                                                                                                                                        "", "", parser.parse_args()


# ==================
# Initializations 2.
# ==================
justify, nt1, nt2, = "".join(list(repeat("\n", 3))), \
                     namedtuple("nt1", "maintitle step title"), \
                     namedtuple("nt2", "artistsort albumsort titlesort discnumber totaldiscs tracknumber totaltracks destination type artist albumartist albumartistsort title titlelanguage object")


# ===============
# Main algorithm.
# ===============
while True:

    #     ----------------------------------------------
    #  1. Grab available artists from current directory.
    #     ----------------------------------------------
    if code == 1:
        header = shared.Header("import  audio  files", ["Set current directory.", "Set artist.", "Set album.", "Set codec.", "Import files.", "Run import.", "Tag files.", "Exit program."])
        head = header()
        tmpl = template1.render(header=nt1(*head), message=['Current directory is: "{0}"'.format(CURWDIR)])
        successes = list()
        statuss.clear()
        files = list()
        args = dict()
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
        artists = [(k, list(v)) for k, v in groupby(AudioFiles.fromfolder(folder=curwdir), key=lambda t: t.artist)]
        kartists = [itemgetter(0)(artist) for artist in artists]
        head = header()
        code = 2
        tmpl = template1.render(header=nt1(*head), list1=kartists)
        if not kartists:
            head = shared.Header("import  audio  files", ["Exit program."], 2)()
            code = 99
            tmpl = template1.render(header=nt1(*head), message=["No artists found."])
        with log1("Found artists.") as title:
            logger.debug(title)
        for artist in log2(kartists):
            logger.debug(artist)

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
        albums = [(k, list(v)) for k, v in groupby(artists[index - 1][1], key=lambda t: t.album)]
        kalbums = [itemgetter(0)(album) for album in albums]
        head = header()
        code = 3
        tmpl = template1.render(header=nt1(*head), list1=kalbums)
        if not kalbums:
            head = shared.Header("import  audio  files", ["Exit program."], 3)()
            code = 99
            tmpl = template1.render(header=nt1(*head), message=['No albums found.'])
        with log1("Found albums.") as title:
            logger.debug(title)
        for album in log2(kalbums):
            logger.debug(album)

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
        codecs = [(k, list(v)) for k, v in groupby(albums[index - 1][1], key=lambda t: t.codec)]
        kcodecs = [itemgetter(0)(codec) for codec in codecs]
        head = header()
        code = 4
        tmpl = template1.render(header=nt1(*head), list1=kcodecs)
        if not kcodecs:
            head = shared.Header("import  audio  files", ["Exit program."], 4)()
            code = 99
            tmpl = template1.render(header=nt1(*head), message=['No codecs found.'])
        with log1("Found codecs.") as title:
            logger.debug(title)
        for codec in log2(codecs):
            logger.debug(codec)

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

        # 4.a. Enumerate available discs.
        discs = dict([(k, list(v)) for k, v in groupby(codecs[index - 1][1], key=lambda t: t.discnumber)])

        # 4.b. Enumerate available files.
        for item in codecs[index - 1][1]:
            track = getattributes(item.object)
            if track:
                files.append((item.file,
                              nt2(mapartistsort(kartists[index - 1]),
                                  track["albumsort"],
                                  track["titlesort"],
                                  track["discnumber"],
                                  str(len(discs)),
                                  track["tracknumber"],
                                  str(len(discs[track["discnumber"]])),
                                  os.path.join(template2.substitute(year=track["year"],
                                                                    month="{0:0>2d}".format(track["month"]),
                                                                    day="{0:0>2d}".format(track["day"]),
                                                                    location=track["location"],
                                                                    disc=track["discnumber"]),
                                               "{0}.{1}{2}".format(track["albumsort"], track["titlesort"], os.path.splitext(item.file)[1])),
                                  item.type,
                                  mapartist(kartists[index - 1]),
                                  mapartist(kartists[index - 1]),
                                  mapartistsort(kartists[index - 1]),
                                  track["title"],
                                  maplanguage(kartists[index - 1]),
                                  item.object
                                  )
                              ))
        files = dict(files)

        # 4.c. Log data structures.

        # -----
        with log1("Found discs.") as title:
            logger.debug(title)
        for num1, item1 in enumerate(sorted(discs), 1):
            logger.debug("{0:>3d}. CD {1}.".format(num1, item1))
            for num2, item2 in enumerate(sorted(discs[item1]), 1):
                logger.debug("\t{0:>3d}.{1:0>2d}. {2}".format(num1, num2, item2.file).expandtabs(3))

        # -----
        with log1("Found files.") as title:
            logger.debug(title)
        for file in log2(sorted(files)):
            logger.debug(file)

            # -----
        with log1("Found tags.") as title:
            logger.debug(title)
        for file in log2(sorted(files)):
            logger.debug(file)
            for tag in "".join(list(files[item].object.pprint())).splitlines():
                logger.debug("\t{0}".format(tag).expandtabs(5))

            logger.debug("")
            logger.debug("\tActual tags.".expandtabs(5))
            logger.debug("\tartistsort\t: {0}".format(files[item].artistsort).expandtabs(5))
            logger.debug("\talbumartistsort: {0}".format(files[item].albumartistsort).expandtabs(5))
            logger.debug("\tartist\t\t: {0}".format(files[item].artist).expandtabs(5))
            logger.debug("\talbumartist\t: {0}".format(files[item].albumartist).expandtabs(5))
            logger.debug("\ttitlesort\t\t: {0}".format(files[item].titlesort).expandtabs(5))
            logger.debug("\tdiscnumber\t: {0}".format(files[item].discnumber).expandtabs(5))
            logger.debug("\ttotaldiscs\t: {0}".format(files[item].totaldiscs).expandtabs(5))
            logger.debug("\ttracknumber\t: {0}".format(files[item].tracknumber).expandtabs(5))
            logger.debug("\ttotaltracks\t: {0}".format(files[item].totaltracks).expandtabs(5))
            logger.debug("\ttitle\t\t: {0}".format(files[item].title).expandtabs(5))
        logger.debug("---------------")
        logger.debug("Available tags.")
        logger.debug("---------------")
        for num, item in enumerate(sorted(files), 1):
            logger.debug("{0:>3d}. {1}".format(num, item))

        logger.debug("---------------")
        logger.debug("Copy arguments.")
        logger.debug("---------------")
        for num, item in enumerate(sorted(files), 1):
            logger.debug("{0:>3d}. {1}".format(num, item))
            logger.debug("\t{0}".format(files[item].destination).expandtabs(5))

        # 4.d. Initialize next screen.
        head = header()
        # code = 5
        code = 99
        tmpl = template1.render(header=nt1(*head),
                                list2=[
                                    (
                                        "Source\t\t: {0}".format(item).expandtabs(TABSIZE2),
                                        "Destination\t: {0}".format(files[item].destination).expandtabs(TABSIZE2)
                                    )
                                    for item in sorted(files)],
                                trailer=["{0:>3d} files ready to be imported.".format(len(files))]
                                )
        if not files:
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
            args.update(files)
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

        # --> 1. Don't run import.
        if choice.upper() == "N":
            head = shared.Header("import  audio  files", ["Exit program."], 7)()
            code = 99
            tmpl = template1.render(header=nt1(*head))

        # --> 2. Run import.
        elif choice.upper() == "Y":

            # --> 2.a. Log data structures.
            logger.debug("---------------------------")
            logger.debug("Accumulated copy arguments.")
            logger.debug("---------------------------")
            for num, item in enumerate(sorted(args), 1):
                logger.debug("{0:>3d}. Source     : {1}".format(num, item))
                logger.debug("\tDestination: {0}".format(args[item].destination).expandtabs(5))

            # --> 2.b. Test mode.
            head = shared.Header("import  audio  files", ["Exit program."], 7)()
            code = 99
            tmpl = template1.render(header=nt1(*head))

            # --> 2.c. Copy mode.
            if not arguments.test:

                # --> 2.c.1. Copy files.
                logger.debug("Start copying files.")
                for item in sorted(args):
                    while True:
                        try:
                            copy2(src=item, dst=args[item].destination)
                        except FileNotFoundError:
                            os.makedirs(os.path.dirname(args[item].destination))
                            logger.debug('"FileNotFound" error raised. Create "{0}"'.format(os.path.dirname(args[item].destination)))
                        except FileExistsError:
                            statuss.append(100)
                            fails.append(item)
                            logger.debug('"FileExists" error raised when tried to copy "{0}".'.format(args[item].destination))
                            break
                        else:
                            statuss.append(0)
                            successes.append((args[item].destination, item))
                            logger.debug('"{0}" copied.'.format(args[item].destination))
                            break
                successes = dict(successes)
                logger.debug("End copying files.")

                # --> 2.c.2. Log results.
                if successes:
                    logger.debug("----------")
                    logger.debug("Successes.")
                    logger.debug("----------")
                    for num, item in enumerate(sorted(successes), 1):
                        logger.debug("{0:>3d}. {1}".format(num, successes[item]))
                if fails:
                    logger.debug("------")
                    logger.debug("Fails.")
                    logger.debug("------")
                    for num, item in enumerate(fails, 1):
                        logger.debug("{0:>3d}. {1}".format(num, item))

                # --> 2.c.3. Tag copied files if at least one copy command succeeded.
                head = header()
                code = 99
                # code = 7
                tmpl = template1.render(header=nt1(*head))

                # --> 2.c.4. Exit program if all copy commands failed.
                if all(map(ne, statuss, repeat(0))):
                    head = shared.Header("import  audio  files", ["Exit program."], 7)()
                    code = 99
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
        # head = shared.Header("import  audio  files", ["Exit program."], 8)()
        head = header()
        code = 99
        tmpl = template1.render(header=nt1(*head))
        if choice.upper() == "Y":
            for file in sorted(successes):
                try:
                    track = files[successes[file]].type(file)
                except MutagenError:
                    pass
                else:
                    track.update([
                        ("artistsort", files[successes[file]].artistsort),
                        ("albumartistsort", files[successes[file]].albumartistsort),
                        ("albumsort", files[successes[file]].albumsort),
                        ("titlesort", files[successes[file]].titlesort),
                        ("taggingtime", shared.dateformat(datetime.now(tz=timezone(shared.DFTTIMEZONE)), shared.TEMPLATE3)),
                        ("source", "CD (Lossless)"),
                        ("disctotal", files[successes[file]].totaldiscs),
                        ("tracktotal", files[successes[file]].totaltracks),
                        ("artist", files[successes[file]].artist),
                        ("albumartist", files[successes[file]].albumartist),
                        ("titlelanguage", files[successes[file]].titlelanguage)
                    ])
                    track.save()
            # code = 99
            # tmpl = template1.render(header=nt1(*head))

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
