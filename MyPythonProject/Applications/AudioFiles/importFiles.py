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
# class Folder(object):
#
#     regex = re.compile(r"\b({year})\b\-\b({month})\b\-\b({day})\b \b([a-z, ]+)$".format(year=shared.DFTYEARREGEX, month=shared.DFTMONTHREGEX, day=shared.DFTDAYREGEX), re.IGNORECASE)
#
#     def __init__(self, fld):
#         self._month = 0
#         self._year = 0
#         self._day = 0
#         self._location = ""
#         self._folder = ""
#         self.folder = fld
#
#     @property
#     def year(self):
#         return self._year
#
#     @property
#     def month(self):
#         return self._month
#
#     @property
#     def day(self):
#         return self._day
#
#     @property
#     def location(self):
#         return self._location
#
#     @property
#     def folder(self):
#         return self._folder
#
#     @folder.setter
#     def folder(self, arg):
#         match = self.regex.search(arg)
#         if not match:
#             raise SyntaxError('"{0}" doesn\'t respect the expected pattern.'.format(arg))
#         self._folder = arg
#         self._year = match.group(1)
#         self._month = match.group(2)
#         self._day = match.group(3)
#         # self._location = match.group(4)


# class Track(object):
#
#     regex = re.compile(r"[a-z]\B(?:1[1-9])(?:{month})(?:{day})d(\d)\B_".format(month=shared.DFTMONTHREGEX, day=shared.DFTDAYREGEX), re.IGNORECASE)
#
#     def __init__(self, s):
#         self._discnumber = 0
#         self.discnumber = s
#
#     @property
#     def discnumber(self):
#         return self._discnumber
#
#     @discnumber.setter
#     def discnumber(self, arg):
#         match = self.regex.search(arg)
#         if not match:
#             raise SyntaxError('"{0}" doesn\'t respect the expected pattern.'.format(arg))
#         self._discnumber = match.group(1)


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
        for key in audio.keys():
            self._metadata[key] = self.fixup(audio[key])
        if "album" not in self._metadata:
            raise TagError(os.path.normpath(arg), "album", "isn\'t available.")
        if "discnumber" not in self._metadata:
            raise TagError(os.path.normpath(arg), "discnumber", "isn\'t available.")
        if "tracknumber" not in self._metadata:
            raise TagError(os.path.normpath(arg), "tracknumber", "isn\'t available.")
        if not self.regex.match(self.metadata["album"]):
            raise TagError(os.path.normpath(arg), "album", "doesn\'t respect the expected pattern.")

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

    regex = re.compile(r"[a-z]\B(?:1[1-9])(?:{month})(?:{day})d(\d)\B_".format(month=shared.DFTMONTHREGEX, day=shared.DFTDAYREGEX), re.IGNORECASE)

    def __init__(self, number=1):
        self._number = 0
        self.number = number

    @property
    def number(self):
        return self._number

    @number.setter
    def number(self, arg):
        self._number = str(arg)

    def __call__(self, path, files):
        o = []
        for fil in files:
            exclude = True
            match = self.regex.search(fil)
            if match:
                exclude = False
                try:
                    assert match.group(1) == self.number
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
        head = header()
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
        head = header()

        #  2.a. Grab metadata from selected folder.
        # try:
        #     src = Folder(list_folders[index - 1])
        # except SyntaxError as err:
        #     code = 99
        #     tmpl = template1.render(header=header, message=list((err,)))

        #  2.b. Then store file destination.
        # else:
        src = list_folders[index - 1]
        # for fil in os.listdir(src):
        #     if fnmatch.fnmatch(fil, "*.{0}".format(arguments.extension.lower())):
        #         track = toto(os.path.join(src, fil))
        #         if track:
                # try:
                #     track = Track(fil)
                # except SyntaxError:
                #     pass
                # else:
                #     tracks.append((fil,
                #                    "{year}{month:0>2d}{day:0>2d}".format(year=track.year, month=track.month, day=track.day),
                #                    track.discnumber,
                #                    template3.substitute(year=track.year, month=track.month, day=track.day, location=track.location, disc=track.discnumber)
                #                    ))
        track = [(
                     fil,
                     "{year}{month:0>2d}{day:0>2d}".format(year=track.year, month=track.month, day=track.day),
                     track.discnumber,
                     template3.substitute(year=track.year, month=track.month, day=track.day, location=track.location, disc=track.discnumber)
                 )
                 for fil, track in map(toto, [os.path.join(src, fil) for fil in os.listdir(src) if fnmatch.fnmatch(fil, "*.{0}".format(arguments.extension.lower()))]) if track
                 ]
        code = 99
        tmpl = template1.render(header=nt(*head), message=list(('No files found in "{0}".'.format(src.folder),)))
        if tracks:
            code = 3
            tmpl = template1.render(header=nt(*head), detail=[(os.path.join(src.folder, itemgetter(0)(item)), os.path.join(itemgetter(2)(item), itemgetter(0)(item))) for item in tracks])

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
            for disc, dst in zip(sorted(map(int, {itemgetter(1)(item) for item in tracks})), sorted({itemgetter(2)(item) for item in tracks})):
                args.append((src.folder, dst, disc))
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
            for src, dst, disc in args:
                if disc is None:
                    copytree(src=src, dst=dst)
                elif disc is not None:
                    copytree(src=src, dst=dst, ignore=InvalidFile(disc))
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
