# -*- coding: ISO-8859-1 -*-
from collections import namedtuple, MutableMapping
from jinja2 import Environment, FileSystemLoader
from mutagen import MutagenError
from operator import itemgetter
from mutagen.flac import FLAC
from string import Template
from functools import wraps
from shutil import copytree
import subprocess
import itertools
import argparse
import fnmatch
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


# ==========
# Arguments.
# ==========
parser = argparse.ArgumentParser()
parser.add_argument("extension")


# ========
# Classes.
# ========
class TagError(MutagenError):
    def __init__(self, fil, tag, msg):
        self.fil = fil
        self.tag = tag
        self.msg = msg


class Track(MutableMapping):

    regex = re.compile(r"^({year})/({month})/({day}) ([^,]+, [a-z]+)$".format(year=shared.DFTYEARREGEX,  month=shared.DFTMONTHREGEX, day=shared.DFTDAYREGEX), re.IGNORECASE)

    def __init__(self, fil):
        self._index = 0
        self._metadata = dict()
        self.metadata = fil

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
    def metadata(self, arg):
        audio = FLAC(arg)
        if "album" not in audio:
            raise TagError(os.path.normpath(arg), "album", "isn\'t available.")
        if "discnumber" not in audio:
            raise TagError(os.path.normpath(arg), "discnumber", "isn\'t available.")
        if "tracknumber" not in audio:
            raise TagError(os.path.normpath(arg), "tracknumber", "isn\'t available.")
        if not self.regex.match(audio["album"]):
            raise TagError(os.path.normpath(arg), "album", "doesn\'t respect the expected pattern.")
        for key in audio:
            self._metadata[key] = self.fixup(audio[key])

    @property
    def discnumber(self):
        return int(self.metadata["discnumber"])

    @property
    def tracknumber(self):
        return int(self.metadata["tracknumber"])

    @property
    def album(self):
        return self.metadata["album"]

    @property
    def year(self):
        match = self.regex.match(self.metadata["album"])
        if match:
            return int(match.group(1))

    @property
    def month(self):
        match = self.regex.match(self.metadata["album"])
        if match:
            return int(match.group(2))

    @property
    def day(self):
        match = self.regex.match(self.metadata["album"])
        if match:
            return int(match.group(3))

    @property
    def location(self):
        match = self.regex.match(self.metadata["album"])
        if match:
            return match.group(4)

    @staticmethod
    def fixup(v):
        if len(v) == 1:
            return v[0]
        return v


class InvalidFile(object):

    def __init__(self, collection, day, location, number):
        self._collection = collection
        self._location = location
        self._number = number
        self._day = day

    def __call__(self, path, fils):
        o = []
        for fil in fils:
            exclude = True
            if fil in collection:
                exclude = False
                try:
                    assert (int("{0}{1}{2}".format(collection[fil].year, collection[fil].month, collection[fil].day)), collection[fil].location, collection[fil].disc) == (self.day, self.location, self.number)
                except AssertionError:
                    exclude = True
            if exclude:
                o.append(fil)
        return o


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


def toto(fil):
    try:
        audiofil = Track(fil)
    except (TagError, MutagenError):
        return fil, None
    return fil, audiofil


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
environment.filters["sortedlist"] = shared.sortedlist
environment.filters["ljustify"] = shared.ljustify
environment.filters["rjustify"] = shared.rjustify


# ===================
# Jinja2 template(s).
# ===================
template1 = environment.get_template("T1")
template2 = environment.get_template("XXCOPY")


# ================
# Local templates.
# ================
template3 = Template(r"F:\S\Springsteen, Bruce\2\$year\$month.$day - $location\CD$disc\1.Free Lossless Audio Codec")


# ==========
# Constants.
# ==========
MODES, CURWDIR, TABSIZE = {"copy": "copied", "import": "imported"}, os.path.join(os.path.expandvars("%_MYMUSIC%"), r"Bruce Springsteen & The E Street Band"), 10


# ==================
# Initializations 1.
# ==================
index, code, status, curwdir, tracks, args, tmpl, choice, src, arguments = 0, 1, 100, CURWDIR, [], [], "", "", None, parser.parse_args()


# ==================
# Initializations 2.
# ==================
justify, nt = "".join(list(itertools.repeat("\n", 3))), namedtuple("nt", "maintitle step title")


# ====================
# Regular expressions.
# ====================
regex = re.compile(r"\b({0})\b\-\b({1})\b\-\b({2})\b \b([a-z, ]+)\\[^\\\.]+\.(?:{3})$".format(shared.DFTYEARREGEX, shared.DFTMONTHREGEX, shared.DFTDAYREGEX, arguments.extension), re.IGNORECASE)


# ===============
# Main algorithm.
# ===============
while True:

    #     ----------------------------------------------
    #  1. Grab available folders from current directory.
    #     ----------------------------------------------
    if code == 1:
        header = shared.Header("import  audio  files", ["Set current directory.", "Set folder.", "Import files.", "Run import.", "Exit program."])
        head = header()
        tmpl = template1.render(header=nt(*head), message=list(('Current directory is: "{0}"'.format(CURWDIR),)))
        tracks.clear()
        while True:
            print(clearscreen(t=tmpl))
            choice = input("{0}\tWould you like to change the current directory [Y/N]? ".format(justify).expandtabs(TABSIZE))
            if choice.upper() in shared.ACCEPTEDANSWERS:
                break
        if choice.upper() == "Y":
            tmpl = template1.render(header=nt(*head))
            while True:
                print(clearscreen(t=tmpl))
                curwdir = input("{0}\tPlease enter directory: ".format(justify).expandtabs(TABSIZE))
                if curwdir:
                    if not os.path.exists(curwdir):
                        tmpl = template1.render(header=nt(*head), message=list(('"{0}" is not a valid directory!'.format(curwdir),)))
                        continue
                    if not os.path.isdir(curwdir):
                        tmpl = template1.render(header=nt(*head), message=list(('"{0}" is not a valid directory!'.format(curwdir),)))
                        continue
                    break
                tmpl = template1.render(header=nt(*head))
        list_folders = sorted({os.path.dirname(file) for file in directorytree(directory=curwdir, rex=regex)})
        head = header()  # On passe à l'étape 2.
        code = 99
        tmpl = template1.render(header=nt(*head), message=list(("No folders found.",)))
        if list_folders:
            code = 2
            tmpl = template1.render(header=nt(*head), menu=enumerate(list_folders, 1))

    #     ---------------------------------
    #  2. Grab available files from folder.
    #     ---------------------------------
    elif code == 2:
        while True:
            print(clearscreen(t=tmpl))
            choice = input("{0}\tPlease choose source folder: ".format(justify).expandtabs(TABSIZE))
            if choice:
                try:
                    index = int(choice)
                except ValueError:
                    tmpl = template1.render(header=nt(*head), menu=enumerate(list_folders, 1), message=list(('"{0}" is not a valid input'.format(choice),)))
                    continue
                else:
                    if index > len(list_folders):
                        tmpl = template1.render(header=nt(*head), menu=enumerate(list_folders, 1), message=list(('"{0}" is not a valid input'.format(choice),)))
                        continue
                    break
            tmpl = template1.render(header=nt(*head), menu=enumerate(list_folders, 1))
        src = list_folders[index - 1]
        tracks = [(
                     fil,
                     track,
                     int("{year}{month:0>2d}{day:0>2d}".format(year=track.year, month=track.month, day=track.day)),
                     track.location,
                     track.discnumber,
                     template3.substitute(year=track.year, month=track.month, day=track.day, location=track.location, disc=track.discnumber)
                 )
                 for fil, track in map(toto, [os.path.join(src, fil) for fil in os.listdir(src) if fnmatch.fnmatch(fil, "*.{0}".format(arguments.extension.lower()))]) if track
                 ]
        files = dict([(itemgetter(0)(item), itemgetter(1)(item)) for item in tracks])
        head = header()  # On passe à l'étape 3.
        code = 99
        tmpl = template1.render(header=nt(*head), message=list(('No files found in "{0}".'.format(src.folder),)))
        if tracks:
            code = 3
            tmpl = template1.render(header=nt(*head), detail=[itemgetter(0)(item), os.path.join(itemgetter(5)(item), os.path.basename(itemgetter(0)(item)))) for item in tracks])

    #     -------------
    #  3. Import files.
    #     -------------
    elif code == 3:
        while True:
            print(clearscreen(t=tmpl))
            choice = input("{0}\tWould you like to import files [Y/N]? ".format(justify).expandtabs(TABSIZE))
            if choice.upper() in shared.ACCEPTEDANSWERS:
                break
        head = header()
        code = 4
        if choice.upper() == "Y":
            for day, location, disc, dst in {(itemgetter(2)(item), itemgetter(3)(item), itemgetter(4)(item), itemgetter(5)(item)) for item in tracks}:
                args.append((src, dst, day, location, disc))
        elif choice.upper() == "N" and not args:
            head = shared.Header("import  audio  files", ["Exit program."], 4)()
            code = 99
        tmpl = template1.render(header=nt(*head))

    #     -----------
    #  4. Run import.
    #     -----------
    elif code == 4:
        while True:
            print(clearscreen(t=tmpl))
            choice = input("{0}\tWould you like to run import [Y/N]? ".format(justify).expandtabs(TABSIZE))
            if choice.upper() in shared.ACCEPTEDANSWERS:
                break
        head = header()
        if choice.upper() == "N":
            code = 99
            tmpl = template1.render(header=nt(*head))
        elif choice.upper() == "Y":
            for src, dst, day, location, disc in args:
                copytree(src=src, dst=dst, ignore=InvalidFile(files, day, location, disc))
            status = 0
            break

    #     -------------
    #  5. Exit program.
    #     -------------
    elif code == 99:
        while True:
            print(clearscreen(t=tmpl))
            choice = input("{0}\tWould you like to exit program [Y/N]? ".format(justify).expandtabs(TABSIZE))
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
