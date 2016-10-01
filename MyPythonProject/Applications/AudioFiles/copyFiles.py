# -*- coding: ISO-8859-1 -*-
import os
import re
import sys
import locale
import logging
import itertools
from pytz import timezone
from string import Template
from functools import wraps
from datetime import datetime
from operator import itemgetter
from subprocess import run, PIPE
from collections import namedtuple
from jinja2 import Environment, FileSystemLoader
from .. import shared

__author__ = 'Xavier ROSSET'


# ==========================
# Define French environment.
# ==========================
locale.setlocale(locale.LC_ALL, "")


# ========
# Logging.
# ========
logger = logging.getLogger("%s.%s" % (__package__, os.path.basename(__file__)))


# ==========
# Constants.
# ==========
ACCEPTEDEXTENSIONS, TEMP, XXCOPYLOG, OUTFILE, TABSIZE = ["flac", "mp3", "m4a", "ogg"], \
                                                        os.path.expandvars("%TEMP%"), \
                                                        os.path.expandvars("%_XXCOPYLOG%"), \
                                                        "xxcopy", \
                                                        10


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
    run("CLS", shell=True)


def getextensions(art, path=shared.MUSIC):
    d, regex = {}, re.compile(r"\b{0}\b".format(art), re.IGNORECASE)
    for a, b, c in os.walk(path):
        if c:
            if regex.search(a):
                for fil in c:
                    ext = os.path.splitext(fil)[1][1:].lower()
                    if ext in ACCEPTEDEXTENSIONS:
                        d[ext] = d.get(ext, 0) + 1
    return d


def getdrives():
    process = run("WMIC LOGICALDISK GET CAPTION", stdout=PIPE, universal_newlines=True)
    if process.returncode == 0:
        for drive in process.stdout.splitlines():
            yield drive.strip()


def trackslist(coll):  # "coll" est un dictionnaire respectant le schéma suivant : {"D1.T06.NNN": (1, 6, "title", "file")}.
    nt = namedtuple("nt", "disc track title file")
    for trackid in sorted(coll):
        track = nt(*coll[trackid])
        yield track.title


def fileslist(coll):  # "coll" est un dictionnaire respectant le schéma suivant : {"D1.T06.NNN": (1, 6, "title", "file")}.
    nt = namedtuple("nt", "disc track title file")
    for trackid in sorted(coll):
        track = nt(*coll[trackid])
        yield track.file


def justify(repeat=2):
    return "".join(list(itertools.repeat("\n", repeat)))


def getparents(f):
    nt = namedtuple("nt", "found destination")
    try:
        fil = shared.Files(f)
    except FileNotFoundError:
        return nt(False, None)
    else:
        return nt(True, os.path.join(fil.parts[1], fil.parts[2]))


# ====================
# Regular expressions.
# ====================
regex1 = re.compile(r"^[a-z ]+$", re.IGNORECASE)
regex2 = re.compile(r"^[A-Z]:$")


# ======================
# Jinja2 environment1(s).
# ======================
environment = Environment(loader=FileSystemLoader(os.path.join(os.path.expandvars("%_pythonproject%"), "Applications", "AudioFiles", "Templates"), encoding=shared.DFTENCODING),
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
template2 = environment.get_template("XXCOPY")


# ==================
# Initializations 1.
# ==================
mode, status, code, tmpl, choice = shared.WRITE, 100, 1, None, None
artist, extension, folder, command, list_indivfiles, files, tracks, drives, somesfilestocopy = "", "", "", "", [], [], [], [], False


# ==================
# Initializations 2.
# ==================
nt1 = namedtuple("nt1", "maintitle step title")
nt2 = namedtuple("nt2", "albumsort album tracks")


# ==================
# Initializations 3.
# ==================
template3 = Template("${drv}\${dir}")


# ==============
# Start logging.
# ==============
logger.info("{0:=^140s}".format(" {0} ".format(shared.dateformat(datetime.now(tz=timezone(shared.DFTTIMEZONE)), shared.TEMPLATE1))))
logger.info('START "{0}".'.format(os.path.basename(__file__)))


# ===============
# Main algorithm.
# ===============
while True:

    #     -----------
    #  1. Set artist.
    #     -----------
    #     Then grab available extensions.
    if code == 1:
        header = shared.Header("copy  audio  files", ["Set artist.", "Set extension.", "Set folder.", "Set files."])
        head = header()
        tmpl = template1.render(header=nt1(*head))
        while True:
            print(clearscreen(t=tmpl))
            artist = input("{0}\tPlease enter artist: ".format(justify(4)).expandtabs(TABSIZE))
            if artist:
                if regex1.match(artist):
                    break
                tmpl = template1.render(header=nt1(*head), message=['"{0}" is not a valid input.'.format(artist)])
                continue
            tmpl = template1.render(header=nt1(*head))
            continue
        extensions = sorted([key.upper() for key in sorted(getextensions(artist).keys())])
        head = header()
        code = 99
        tmpl = template1.render(header=nt1(*head), message=['No audio files found for "{0}".'.format(artist)])
        if extensions:
            code = 2
            tmpl = template1.render(header=nt1(*head), list1=extensions)

    #     --------------
    #  2. Set extension.
    #     --------------
    #     Then grab available albums.
    elif code == 2:
        while True:
            print(clearscreen(t=tmpl))
            try:
                choice = int(input("{0}\tPlease choose extension: ".format(justify()).expandtabs(TABSIZE)))
            except ValueError:
                continue
            else:
                if choice > len(extensions):
                    continue
                break
        extension = extensions[choice-1]
        collection = shared.AudioFiles.fromfolder(extension, folder=shared.MUSIC)
        try:
            albums = list(collection(extension, key="artist", value=[artist]))
        except ValueError as err:
            header = shared.Header("copy  audio  files", ["Exit program."], 3)
            code = 99
            tmpl = template1.render(header=nt1(*header()), message=[err])
        else:
            code += 1
            tmpl = template1.render(header=nt1(*header()), list1=[itemgetter(1)(item) for item in albums])

    #     ----------
    #  3. Set album.
    #     ----------
    #     Then grab available tracks.
    elif code == 3:
        while True:
            print(clearscreen(t=tmpl))
            try:
                choice = int(input("{0}\tPlease choose album: ".format(justify()).expandtabs(TABSIZE)))
            except ValueError:
                continue
            else:
                if choice > len(albums):
                    continue
                break
        album = nt2(*albums[choice-1])

        # Files list.
        files = list(fileslist(album.tracks))  # liste respectant le schéma : ["file1", "file2", "file3"]
        logger.debug("Selected files")
        for file in files:
            logger.debug('"{0}"'.format(os.path.normpath(file)))

        # tracks list
        tracks = list(trackslist(album.tracks))
        logger.debug("Selected tracks")
        for track in tracks:
            logger.debug('"{0}"'.format(track))

        code += 1
        tmpl = template1.render(header=nt1(*header()), list1=tracks)

    #     -----------
    #  4. Set tracks.
    #     -----------
    #     Then grab available destination drives.
    elif code == 4:
        while True:
            print(clearscreen(t=tmpl))
            choice = input("{0}\tWould you like to select individual files [Y/N]? ".format(justify()).expandtabs(TABSIZE))
            if choice.upper() in shared.ACCEPTEDANSWERS:
                break
        drives = [drive for drive in getdrives() if regex2.match(drive)]

        #  4a. Global.
        if choice.upper() in ["N", "Y"]:
            header = shared.Header("copy  audio  files", ["Set destination drive.", "Copy files.", "Run copy command(s).", "Exit program."], 5)
            mode_files = "G"
            head = header()
            tmpl = template1.render(header=nt1(*head), message=["An issue was encountered while grabbing available destination drives."])
            code = 99
            if drives:
                tmpl = template1.render(header=nt1(*head), list1=drives)
                code = 6

    #  4a. Individual.
        # elif choice.upper() == "Y":
            # header = shared.Header("copy  audio  files", ["Set individual files.", "Set destination drive.", "Copy files.", "Run copy command(s).", "Exit program."], 5)
            # mode_files = "I"
            # head = header()
            # tmpl = template1.render(header=nt1(*head), list1=tracks)
            # code += 1

    #     ---------------------
    #  5. Set individual files.
    #     ---------------------
    #     Then grab available destination drives.
    # elif code == 5:
        # while True:
            # print(clearscreen(t=tmpl))
            # choice = input("{0}\tPlease enter file index [e.g. 1, 2, 5-7, 10]: ".format("".join(list(itertools.repeat("\n", 2)))).expandtabs(TABSIZE))
            # if choice:
                # list_indivfiles = [itemgetter(1)(fil) for fil in tracks if itemgetter(0)(fil) in map(int, s2.formatindexes(choice))]
                # if list_indivfiles:
                    # break
                # tmpl = template1.render(header=nt1(*head), list1=tracks, message=list(("No correct indexes selected.",)))
                # continue
        # list_indivfiles = list(enumerate(sorted(list_indivfiles), start=1))
        # head = header()
        # code = 99
        # tmpl = template1.render(header=nt1(*head), message=list(("An issue was encountered while grabbing available destination drives.",)))
        # if drives:
            # code = 6
            # tmpl = template1.render(header=nt1(*head), list1=drives)

    #     ----------------------
    #  6. Set destination drive.
    #     ----------------------
    #     Then write copy command to temporary working file.
    elif code == 6:
        while True:
            print(clearscreen(t=tmpl))
            try:
                choice = int(input("{0}\tPlease choose destination drive: ".format(justify()).expandtabs(TABSIZE)))
            except ValueError:
                continue
            else:
                if choice > len(drives):
                    continue
                break
        # drive = drives[choice-1]
        files = [(file, os.path.normpath(template3.substitute(drv=drives[choice-1], dir=getparents(file).destination))) for file in files if getparents(file).found]
        # liste respectant le schéma : [("src1", "dst1"), ("src2", "dst2"), ("src3", "dst3")]
        logger.debug("Destination files")
        for src, dst in files:
            logger.debug('"{0}"'.format(os.path.normpath(src)))
            logger.debug('"{0}"'.format(os.path.normpath(dst)))
        code = 99
    #     # directory = "{0}{1}".format(os.path.normpath(os.path.join("{0}{1}".format(drives[choice-1][1], os.path.sep), list_parents[1], list_parents[2])), os.path.sep)
    #     if mode_files == "G":
    #         command = list(enumerate(list((template2.render(src=os.path.normpath("{0}{1}*.{2}".format(album, os.path.sep, extension.lower())),
    #                                                         dst=directory,
    #                                                         dir=TEMP,
    #                                                         lst="xxcopy.lst",
    #                                                         log=XXCOPYLOG),)),
    #                                  start=1
    #                                  )
    #                        )
    #     elif mode_files == "I":
    #         command = list(enumerate(sorted([template2.render(src=fil,
    #                                                           dst=directory,
    #                                                           dir=TEMP,
    #                                                           lst="xxcopy.lst",
    #                                                           log=XXCOPYLOG) for num, fil in list_indivfiles]),
    #                                  start=1
    #                                  )
    #                        )
    #     code += 1
    #     tmpl = template1.render(header=nt1(*header()), list1=command)

    #     ---------------------------------------------
    #  7. Write copy command to temporary working file.
    #     ---------------------------------------------
    #     Then run copy command(s).
    elif code == 7:
        while True:
            print(clearscreen(t=tmpl))
            choice = input("{0}\tWould you like to copy files using the command(s) above [Y/N]? ".format(justify()).expandtabs(TABSIZE))
            if choice.upper() in shared.ACCEPTEDANSWERS:
                break
        code += 1
        if choice.upper() == "Y":
            with open(os.path.join(TEMP, OUTFILE), mode=mode, encoding=shared.DFTENCODING) as fw:
                for num, cmd in command:
                    fw.write("{0}\n".format(cmd))
            somesfilestocopy = True
            mode = shared.APPEND
            tmpl = template1.render(header=nt1(*header()))
        elif choice.upper() == "N" and somesfilestocopy:
            tmpl = template1.render(header=nt1(*header()))
        elif choice.upper() == "N" and not somesfilestocopy:
            header = shared.Header("copy  audio  files", ["Exit program."], 8)
            head = header()
            tmpl = template1.render(header=nt1(*head))
            code = 99

    #     -----------------
    #  8. Run copy command.
    #     -----------------
    elif code == 8:
        while True:
            print(clearscreen(t=tmpl))
            choice = input("{0}\tWould you like to run copy command(s) [Y/N]? ".format(justify()).expandtabs(TABSIZE))
            if choice.upper() in shared.ACCEPTEDANSWERS:
                break
        if choice.upper() == "Y":
            status = 0
            break
        elif choice.upper() == "N":
            code = 99
            tmpl = template1.render(header=nt1(*header()))

    #     -------------
    #  9. Exit program.
    #     -------------
    elif code == 99:
        while True:
            print(clearscreen(t=tmpl))
            choice = input("{0}\tWould you like to exit program [Y/N]? ".format(justify()).expandtabs(TABSIZE))
            if choice.upper() in shared.ACCEPTEDANSWERS:
                break
        if choice.upper() == "Y":
            status = 99
            break
        elif choice.upper() == "N":
            code = 1


# =============
# Exit program.
# =============
sys.exit(status)
